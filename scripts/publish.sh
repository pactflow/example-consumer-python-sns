#!/bin/sh

set -e

echo "finding topic"
TOPIC_ARN=$(aws sns list-topics --output json | grep pactflow-example-consumer-python-sns-ProductEvent | cut -d'"' -f4)
echo "have topic: ${TOPIC_ARN}, publishing message"
aws sns publish --topic-arn "${TOPIC_ARN}" --message "{\"id\": \"some-uuid-1234-5678\", \"type\": \"Product Range\", \"name\": \"Some Product\", \"event\": \"UPDATED\" }"
npm run logs