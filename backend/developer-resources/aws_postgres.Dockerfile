FROM amazonlinux:2 AS installer

ADD "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"  awscliv2.zip
RUN yum update -y \
	&& yum install -y unzip \
	&& unzip awscliv2.zip \
	# The --bin-dir is specified so that we can copy the
	# entire bin directory from the installer stage into
	# into /usr/local/bin of the final stage without
	# accidentally copying over any other executables that
	# may be present in /usr/local/bin of the installer stage.
	&& ./aws/install --bin-dir /aws-cli-bin/ \
	&& yum install -y shadow-utils \
	&& yum clean all

# Create a dedicated user and group for your application
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1001 -d /home/appuser -s /sbin/nologin appuser

# Switch to the non-root user
USER appuser

FROM amazonlinux:2

RUN yum update -y \
	&& yum install -y less groff gzip shadow-utils \
	&& yum clean all
COPY --from=installer /usr/local/aws-cli/ /usr/local/aws-cli/
COPY --from=installer /aws-cli-bin/ /usr/local/bin/

RUN amazon-linux-extras install -y postgresql14 vim epel \
	# Create a dedicated user and group for your application
	&& groupadd -r appgroup && useradd -r -g appgroup -u 1001 -d /home/appuser -s /sbin/nologin appuser

# Switch to the non-root user
USER appuser
