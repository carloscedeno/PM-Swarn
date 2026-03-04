# Redpanda Developer Guide

This guide covers how to connect to Redpanda from your local machine
and use it from application code.

Redpanda runs on a private ECS EC2 node inside the VPC. There is no public endpoint.
All local access goes through the bastion host via SSH tunnels.

---

## Infrastructure Reference

| Resource | Value |
|---|---|
| Bastion host (public IP) | `52.90.62.143` |
| Bastion SSH key | `dev-ssh-tunnel.pem` (get from 1Password) |
| Bastion SSH user | `ec2-user` |
| Redpanda EC2 node | dynamic private IP — fetched via AWS CLI (see below) |
| Kafka broker | `localhost:9092` (after tunnel) |
| Schema Registry | `localhost:8081` (after tunnel) |
| ECS cluster | `aws-agents-dev` |
| AWS profile | `avanto` |
| AWS region | `us-east-1` |

> The Redpanda EC2 node has a dynamic private IP that can change when the instance
> is replaced by the Auto Scaling Group. Always fetch it fresh before opening tunnels.

---

## Prerequisites

### 1. SSH key

Get `dev-ssh-tunnel.pem` from 1Password and save it to `~/.ssh/`:

```bash
chmod 600 ~/.ssh/dev-ssh-tunnel.pem
```

### 2. AWS CLI

```bash
pip install awscli

# Configure the avanto profile
aws configure --profile avanto
# or SSO:
aws sso login --profile avanto
```

### 3. rpk CLI (optional — for topic management from your laptop)

```bash
# macOS
brew install redpanda-data/tap/redpanda

# Linux
curl -LO https://github.com/redpanda-data/redpanda/releases/latest/download/rpk-linux-amd64.zip
unzip rpk-linux-amd64.zip -d ~/.local/bin/
chmod +x ~/.local/bin/rpk
```

---

## Open SSH Tunnel

The tunnel forwards local ports through the bastion to Redpanda inside the VPC.
Run this in a dedicated terminal and keep it open while developing.

> **Important:** Redpanda runs in ECS `awsvpc` mode. The ECS task has its own
> dedicated network interface with a private IP that is **different from the EC2
> host IP** and changes on every task replacement. Always fetch the task IP, not
> the EC2 instance IP.

```bash
export AWS_PROFILE=avanto
export AWS_REGION=us-east-1

BROKER_IP=$(aws ecs describe-tasks \
  --cluster aws-agents-dev \
  --tasks $(aws ecs list-tasks \
    --cluster aws-agents-dev \
    --service-name redpanda-dev-redpanda \
    --query 'taskArns[0]' --output text) \
  --query 'tasks[0].attachments[0].details[?name==`privateIPv4Address`].value' \
  --output text)

echo "Broker task IP: $BROKER_IP"

ssh -i ~/.ssh/dev-ssh-tunnel.pem \
  -L 9092:${BROKER_IP}:9092 \
  -L 8081:${BROKER_IP}:8081 \
  ec2-user@52.90.62.143 -N
```

While this terminal is running:
- Kafka clients → `localhost:9092`
- Schema Registry → `http://localhost:8081`

### Convenience script

Save as `~/scripts/redpanda-tunnel.sh` and `chmod +x`:

```bash
#!/bin/bash
set -e

export AWS_PROFILE=avanto
export AWS_REGION=us-east-1

echo "Fetching Redpanda task IP..."

BROKER_IP=$(aws ecs describe-tasks \
  --cluster aws-agents-dev \
  --tasks $(aws ecs list-tasks \
    --cluster aws-agents-dev \
    --service-name redpanda-dev-redpanda \
    --query 'taskArns[0]' --output text) \
  --query 'tasks[0].attachments[0].details[?name==`privateIPv4Address`].value' \
  --output text)

echo "Broker task IP: $BROKER_IP"
echo ""
echo "Tunnels:"
echo "  localhost:9092  ->  Kafka broker"
echo "  localhost:8081  ->  Schema Registry"
echo ""
echo "Press Ctrl+C to close."

ssh -i "$HOME/.ssh/dev-ssh-tunnel.pem" \
  -L 9092:${BROKER_IP}:9092 \
  -L 8081:${BROKER_IP}:8081 \
  ec2-user@52.90.62.143 -N
```

---

## Connecting from Application Code

Get the `app-agent` password from 1Password (vault: Orderbahn Dev).

### Connection settings

| Setting | Local dev (tunnel open) | ECS service (inside VPC) |
|---|---|---|
| Bootstrap brokers | `localhost:9092` | `redpanda.agentic.local:9092` |
| SASL mechanism | `SCRAM-SHA-256` | `SCRAM-SHA-256` |
| Username | `app-agent` | from Secrets Manager `redpanda-dev-app-agent` |
| Password | from 1Password | from Secrets Manager `redpanda-dev-app-agent` |
| Schema Registry | `http://localhost:8081` | `http://redpanda.agentic.local:8081` |

### Python — confluent-kafka

```python
from confluent_kafka import Producer, Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient

KAFKA_CONFIG = {
    "bootstrap.servers": "localhost:9092",  # redpanda.agentic.local:9092 on ECS
    "security.protocol": "SASL_PLAINTEXT",
    "sasl.mechanism": "SCRAM-SHA-256",
    "sasl.username": "app-agent",
    "sasl.password": "<app-agent-password>",
}

producer = Producer(KAFKA_CONFIG)
producer.produce("my-topic", key="key1", value='{"event": "test"}')
producer.flush()

consumer = Consumer({
    **KAFKA_CONFIG,
    "group.id": "my-consumer-group",
    "auto.offset.reset": "earliest",
})
consumer.subscribe(["my-topic"])

sr = SchemaRegistryClient({
    "url": "http://localhost:8081",  # http://redpanda.agentic.local:8081 on ECS
    "basic.auth.user.info": "app-agent:<app-agent-password>",
})
```

### Python — kafka-python

```python
from kafka import KafkaProducer, KafkaConsumer

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username="app-agent",
    sasl_plain_password="<app-agent-password>",
)
producer.send("my-topic", b'{"event": "test"}')
producer.flush()

consumer = KafkaConsumer(
    "my-topic",
    bootstrap_servers=["localhost:9092"],
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username="app-agent",
    sasl_plain_password="<app-agent-password>",
    group_id="my-consumer-group",
    auto_offset_reset="earliest",
)
for msg in consumer:
    print(msg.value)
```

### Node.js — kafkajs

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  brokers: ['localhost:9092'], // redpanda.agentic.local:9092 on ECS
  sasl: {
    mechanism: 'scram-sha-256',
    username: 'app-agent',
    password: '<app-agent-password>',
  },
});

const producer = kafka.producer();
await producer.connect();
await producer.send({
  topic: 'my-topic',
  messages: [{ key: 'key1', value: JSON.stringify({ event: 'test' }) }],
});
await producer.disconnect();
```

---

## Environment Variables for Local Development

Add to your `.env` file — **never commit this file**:

```bash
KAFKA_BROKERS=localhost:9092
KAFKA_USERNAME=app-agent
KAFKA_PASSWORD=<app-agent-password>
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
SCHEMA_REGISTRY_URL=http://localhost:8081
```

On ECS these are injected automatically via Secrets Manager — no `.env` needed.

---

## rpk — Topic and Consumer Group Commands

With the tunnel open, you can use `rpk` from your laptop to inspect topics and
consumer group lag. Use your `app-agent` credentials.

```bash
APP_PASS=<app-agent-password>

# List topics
rpk topic list \
  -X brokers=localhost:9092 \
  -X user=app-agent -X pass="$APP_PASS" \
  -X sasl.mechanism=SCRAM-SHA-256

# Produce a test message
echo '{"event":"test"}' | rpk topic produce my-topic \
  -X brokers=localhost:9092 \
  -X user=app-agent -X pass="$APP_PASS" \
  -X sasl.mechanism=SCRAM-SHA-256

# Consume messages (latest 10)
rpk topic consume my-topic --num 10 \
  -X brokers=localhost:9092 \
  -X user=app-agent -X pass="$APP_PASS" \
  -X sasl.mechanism=SCRAM-SHA-256

# Consumer group lag
rpk group list \
  -X brokers=localhost:9092 \
  -X user=app-agent -X pass="$APP_PASS" \
  -X sasl.mechanism=SCRAM-SHA-256

rpk group describe <group-name> \
  -X brokers=localhost:9092 \
  -X user=app-agent -X pass="$APP_PASS" \
  -X sasl.mechanism=SCRAM-SHA-256
```

### Save an rpk profile (skip -X flags on every command)

```bash
rpk profile create redpanda-dev \
  --set brokers=localhost:9092 \
  --set user=app-agent \
  --set pass="$APP_PASS" \
  --set sasl.mechanism=SCRAM-SHA-256

rpk profile use redpanda-dev

# Now run without -X flags:
rpk topic list
rpk group list
```

---

## Troubleshooting

### "Connection refused" on localhost:9092 or localhost:8081

The SSH tunnel is not running. Open it (see "Open SSH Tunnel" above).

### "Authentication failed"

Your password is wrong. Get the correct `app-agent` password from 1Password.

### Broker IP changed (tunnel fails after task replacement)

The Redpanda ECS task was replaced and got a new IP. Re-run the tunnel
script — it fetches the current task IP automatically each time.

### Verify the tunnel is working

```bash
# Schema Registry — list registered schemas
curl -s http://localhost:8081/subjects

# Kafka — connect with rpk
rpk topic list \
  -X brokers=localhost:9092 \
  -X user=app-agent -X pass="$APP_PASS" \
  -X sasl.mechanism=SCRAM-SHA-256
```

### View broker logs (read-only, no credentials needed)

```bash
aws logs tail /ecs/redpanda-dev --since 15m --format short \
  --profile avanto --region us-east-1
```
