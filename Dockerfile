# Stage 1: Builder
FROM python:3.11 AS builder

# Improve performance and prevent generation of .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Create and activate a virtual environment, then install the dependencies
RUN pip install virtualenv && \
    virtualenv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Deployer
FROM python:3.11 AS deployer

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# install Microsoft SQL Server requirements.
ENV ACCEPT_EULA=Y

RUN apt-get clean && \
    apt-get update --allow-releaseinfo-change && \
    apt-get install -y --no-install-recommends curl gnupg

# Reset the APT keyring to remove invalid signatures
RUN rm -rf /etc/apt/keyrings && mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/keyrings/microsoft.asc > /dev/null && \
    apt-key add /etc/apt/keyrings/microsoft.asc

# Add SQL Server ODBC Driver 17 for Ubuntu 18.04
RUN echo "deb [signed-by=/etc/apt/keyrings/microsoft.asc] https://packages.microsoft.com/debian/10/prod buster main" | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql17 mssql-tools && \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile && \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# clean the install.
RUN apt-get -y clean


# Set the working directory
WORKDIR /app

# Copy the rest of the application code
COPY . .

EXPOSE 8001

# CMD ["python3", "main.py", "--config", "./config.yaml", "llm"]
