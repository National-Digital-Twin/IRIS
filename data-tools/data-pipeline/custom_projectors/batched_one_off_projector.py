from typing import Protocol

from telicent_lib.logging import CoreLoggerAdapter, CoreLoggerFactory
from telicent_lib.sinks import KafkaSink
from telicent_lib.sources import KafkaSource


class BatchedOneOffProjector:
    def __init__(
        self,
        source_topic: str,
        kafka_consumer_config: dict,
        kafka_producer_config: dict,
        batch_size: int,
        projection_function: Protocol,
    ):
        self.source_topic = source_topic
        self.kafka_consumer_config = kafka_consumer_config
        self.kafka_producer_config = kafka_producer_config
        self.batch_size = batch_size
        self.projection_function = projection_function

    def run(self):
        logger = self.__create_logger()

        logger.info(
            f"Processing records in {self.source_topic} with a batch size of {self.batch_size}..."
        )

        with KafkaSource(
            topic=self.source_topic,
            kafka_config=self.kafka_consumer_config,
        ) as source:
            with KafkaSink(
                topic=f"{self.source_topic}-projected-dlq",
                kafka_config=self.kafka_producer_config,
            ) as target_dlq:
                self.__process_records(source, target_dlq, logger)

    def __process_records(self, source, target_dlq, logger: CoreLoggerAdapter) -> None:
        total_records_to_project = source.remaining()
        total_records_processed = 0
        total_records_sent_to_dlq = 0
        batch = []

        for index, record in enumerate(source.data()):
            if total_records_to_project is None:
                total_records_to_project = source.remaining()

            (
                total_records_processed,
                total_records_sent_to_dlq,
                should_stop,
            ) = self.__process_record(
                index=index,
                record=record,
                batch=batch,
                source=source,
                target_dlq=target_dlq,
                logger=logger,
                total_records_processed=total_records_processed,
                total_records_sent_to_dlq=total_records_sent_to_dlq,
                total_records_to_project=total_records_to_project,
            )

            if should_stop:
                logger.info(
                    f"Finished processing all records in {self.source_topic}!"
                )
                break

    def __process_record(
        self,
        index: int,
        record,
        batch: list,
        source,
        target_dlq,
        logger: CoreLoggerAdapter,
        total_records_processed: int,
        total_records_sent_to_dlq: int,
        total_records_to_project: int,
    ) -> tuple[int, int, bool]:
        try:
            batch.append(record)
            if self.__is_batch_ready(batch):
                total_records_processed += len(batch)
                self.__project_batch(batch)

            if self.__is_final_record_with_pending_batch(
                index, total_records_to_project, batch
            ):
                total_records_processed += len(batch)
                self.__project_batch(batch)

            self.__log_progress(
                logger,
                index,
                total_records_sent_to_dlq,
                source,
            )
        except Exception as err:
            logger.error(f"Error occured at offset {index}: {err}")
            total_records_sent_to_dlq += self.__send_batch_to_dlq(target_dlq, batch)

        should_stop = self.__is_finished(
            total_records_processed,
            total_records_to_project,
            source,
        )
        return total_records_processed, total_records_sent_to_dlq, should_stop

    def __is_batch_ready(self, batch: list) -> bool:
        return len(batch) % self.batch_size == 0

    def __project_batch(self, batch: list) -> None:
        self.projection_function(batch)
        batch.clear()

    def __is_final_record_with_pending_batch(
        self, index: int, total_records_to_project: int, batch: list
    ) -> bool:
        return index == total_records_to_project and len(batch) > 0

    def __is_finished(
        self, total_records_processed: int, total_records_to_project: int, source
    ) -> bool:
        return (
            total_records_processed >= total_records_to_project
            and source.remaining() == 0
        )

    def __send_batch_to_dlq(self, target_dlq, batch: list) -> int:
        sent_count = 0
        for batch_record in batch:
            target_dlq.send(batch_record)
            sent_count += 1
        batch.clear()
        return sent_count

    def __log_progress(
        self, logger: CoreLoggerAdapter, index: int, total_records_sent_to_dlq: int, source
    ) -> None:
        if index > 0 and index % 25000 == 0:
            logger.info(
                f"Processed {index} records, {total_records_sent_to_dlq} records sent to DLQ, {source.remaining()} records remaining"
            )

    def __create_logger(self) -> CoreLoggerAdapter:
        return CoreLoggerFactory.get_logger(
            f"{self.source_topic}-projected-logger",
            kafka_config=self.kafka_producer_config,
            topic=f"{self.source_topic}-to-projected-logging",
        )
