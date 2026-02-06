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
                total_records_to_project = source.remaining()
                total_records_processed = 0
                total_records_sent_to_dlq = 0
                batch = []
                for index, record in enumerate(source.data()):
                    try:
                        if total_records_to_project is None:
                            total_records_to_project = source.remaining()

                        batch.append(record)

                        total_records_processed = self.__project_full_batch_if_ready(
                            batch, total_records_processed
                        )

                        self.__log_progress_if_needed(
                            logger, source, index, total_records_sent_to_dlq
                        )

                        total_records_processed = self.__project_trailing_batch_if_needed(
                            index, total_records_to_project, batch, total_records_processed
                        )

                        if self.__is_finished(
                            source, total_records_processed, total_records_to_project
                        ):
                            self.__log_finished(logger)
                            break

                    except Exception as err:
                        logger.error(f"Error occured at offset {index}: {err}")

                        total_records_sent_to_dlq = self.__send_batch_to_dlq(
                            target_dlq, batch, total_records_sent_to_dlq
                        )

                        if self.__is_finished(
                            source, total_records_processed, total_records_to_project
                        ):
                            self.__log_finished(logger)
                            break

    def __create_logger(self) -> CoreLoggerAdapter:
        return CoreLoggerFactory.get_logger(
            f"{self.source_topic}-projected-logger",
            kafka_config=self.kafka_producer_config,
            topic=f"{self.source_topic}-to-projected-logging",
        )

    def __project_full_batch_if_ready(
        self, batch: list, total_records_processed: int
    ) -> int:
        if len(batch) % self.batch_size == 0:
            total_records_processed += self.batch_size
            self.projection_function(batch)
            batch.clear()
        return total_records_processed

    def __project_trailing_batch_if_needed(
        self,
        index: int,
        total_records_to_project: int,
        batch: list,
        total_records_processed: int,
    ) -> int:
        if index == total_records_to_project and len(batch) > 0:
            total_records_processed += len(batch)
            self.projection_function(batch)
            batch.clear()
        return total_records_processed

    def __log_progress_if_needed(
        self,
        logger: CoreLoggerAdapter,
        source: KafkaSource,
        index: int,
        total_records_sent_to_dlq: int,
    ) -> None:
        if index > 0 and index % 25000 == 0:
            logger.info(
                f"Processed {index} records, {total_records_sent_to_dlq} records sent to DLQ, {source.remaining()} records remaining"
            )

    def __send_batch_to_dlq(
        self, target_dlq: KafkaSink, batch: list, total_records_sent_to_dlq: int
    ) -> int:
        for batch_record in batch:
            target_dlq.send(batch_record)
            total_records_sent_to_dlq += 1
        batch.clear()
        return total_records_sent_to_dlq

    def __is_finished(
        self, source: KafkaSource, total_records_processed: int, total_records_to_project: int
    ) -> bool:
        return (
            total_records_processed >= total_records_to_project
            and source.remaining() == 0
        )

    def __log_finished(self, logger: CoreLoggerAdapter) -> None:
        logger.info(f"Finished processing all records in {self.source_topic}!")
