# Example Python AWS SNS Consumer

[![Build Status](https://github.com/pactflow/example-consumer-python-sns/actions/workflows/build.yml/badge.svg)](https://github.com/pactflow/example-consumer-python-sns/actions)

[![Can I deploy Status](https://test.pactflow.io/pacticipants/pactflow-example-consumer-python-sns/branches/master/latest-version/can-i-deploy/to-environment/production/badge.svg)](https://test.pactflow.io/pacticipants/pactflow-example-consumer-python-sns/branches/master/latest-version/can-i-deploy/to-environment/production/badge)

[![Pact Status](https://test.pactflow.io/pacts/provider/pactflow-example-provider-python-sns/consumer/pactflow-example-consumer-python-sns/latest/badge.svg?label=consumer)](https://test.pactflow.io/pacts/provider/pactflow-example-provider-python-sns/consumer/pactflow-example-consumer-python-sns/latest) (latest pact)

[![Pact Status](https://test.pactflow.io/matrix/provider/pactflow-example-provider-python-sns/latest/master/consumer/pactflow-example-consumer-python-sns/latest/master/badge.svg?label=consumer)](https://test.pactflow.io/pacts/provider/pactflow-example-provider-python-sns/consumer/pactflow-example-consumer-python-sns/latest/prod) (prod/prod pact)

This is an example of a Python AWS SNS consumer that uses Pact, [Pactflow](https://pactflow.io) and GitHub Actions to ensure that it is compatible with the expectations its consumers have of it.

All examples in the series `example-consumer-<language>-sns` provide the same functionality to be easily comparable across languages.
As such, please refer to [https://docs.pactflow.io/docs/examples/aws/sns/consumer/](AWS SNS Consumer Examples) to avoid unnecessary duplication of details here.

Language specific sections which differ from the canonical example only can be found below.

### How to write tests?

We recommend that you split the code that is responsible for handling the protocol specific things - in this case the lambda and SNS input - and the piece of code that actually handles the payload.

You're probably familiar with layered architectures such as Ports and Adaptors (also referred to as a Hexagonal architecture). Following a modular architecture will allow you to do this much more easily:

![Code Modularity](docs/ports-and-adapters.png "Code Modularity")

This code base is setup with this modularity in mind:

* [Lambda Handler](src/_lambda/product.py)
* [Event Service](src/product/product_service.py)
* Business Logic
    * [Product](src/product/product.py)
    * [Repository](src/product/product_repository.py)

The target of our [consumer pact test](tests/unit/product_service_pact_test.py) is the [Event Service](src/product/product_service.js), which is responsible for consuming a Product update event, and persisting it to a database (the Repository).

See also:

* https://dius.com.au/2017/09/22/contract-testing-serverless-and-asynchronous-applications/
* https://dius.com.au/2018/10/01/contract-testing-serverless-and-asynchronous-applications---part-2/

## Usage
### Testing

* Run the unit tests: `make test`
* Run a (local) lambda integration test: `make integration`

### Running

* Deploy the actual app: `make deploy` (see below for more background)
* Publish a test event: `make publish`
* View the lambda logs: `make logs`

Here is some sample output publishing and viewing the logs:
```
➜  example-consumer-js-sns git:(master) ✗ npm run publish                                                                                                                                                                                                                                                    <aws:pact-dev>

> product-service@1.0.0 publish /Users/matthewfellows/development/public/example-consumer-js-sns
> ./scripts/publish.sh

finding topic
have topic: arn:aws:sns:ap-southeast-2:838728264948:pactflow-example-consumer-js-sns-ProductEvent-144XVHN8QP2D3, publishing message
{
    "MessageId": "735a2daa-7eaa-53d7-b362-75b0d9227708"
}

> product-service@1.0.0 logs /Users/matthewfellows/development/public/example-consumer-js-sns
> sam logs -n ProductEventHandler --stack-name pactflow-example-consumer-js-sns -t

2020/11/03/[$LATEST]df9d6b71ef1e49789f4ebca64fc19270 2020-11-03T00:25:24.984000 START RequestId: 47e97e7d-52cf-4c83-9133-545749ed2750 Version: $LATEST
2020/11/03/[$LATEST]df9d6b71ef1e49789f4ebca64fc19270 2020-11-03T00:25:25.012000 2020-11-03T00:25:24.988Z	47e97e7d-52cf-4c83-9133-545749ed2750	INFO	{
  Records: [
    {
      EventSource: 'aws:sns',
      EventVersion: '1.0',
      EventSubscriptionArn: 'arn:aws:sns:ap-southeast-2:838728264948:pactflow-example-consumer-js-sns-ProductEvent-144XVHN8QP2D3:efaf0845-3847-4b5d-a4b1-68f33ef524e8',
      Sns: [Object]
    }
  ]
}
2020/11/03/[$LATEST]df9d6b71ef1e49789f4ebca64fc19270 2020-11-03T00:25:25.032000 END RequestId: 47e97e7d-52cf-4c83-9133-545749ed2750
2020/11/03/[$LATEST]df9d6b71ef1e49789f4ebca64fc19270 2020-11-03T00:25:25.032000 REPORT RequestId: 47e97e7d-52cf-4c83-9133-545749ed2750	Duration: 48.28 ms	Billed Duration: 100 ms	Memory Size: 128 MB	Max Memory Used: 64 MB	Init Duration: 136.98 ms
```

If you edit the file `./scripts/publish.sh` to remove a valid property, or upload invalid JSON you will get something like this:

```
2020/11/03/[$LATEST]df9d6b71ef1e49789f4ebca64fc19270 2020-11-03T00:36:23.376000 2020-11-03T00:36:23.376Z	3eb496cd-c663-4ae2-a717-8f261b7ad48c	ERROR	Invoke Error 	{"errorType":"AssertionError","errorMessage":"id is a mandatory field","code":"ERR_ASSERTION","generatedMessage":false,"expected":true,"operator":"==","stack":["AssertionError [ERR_ASSERTION]: id is a mandatory field","    at new Product (/var/task/src/product/product.js:5:5)","    at handler (/var/task/src/product/product.handler.js:7:23)","    at /var/task/src/service/product.js:10:44","    at Array.map (<anonymous>)","    at Runtime.lambda [as handler] (/var/task/src/service/product.js:10:33)","    at Runtime.handleOnce (/var/runtime/Runtime.js:66:25)"]}
2020/11/03/[$LATEST]df9d6b71ef1e49789f4ebca64fc19270 2020-11-03T00:36:23.416000 END RequestId: 3eb496cd-c663-4ae2-a717-8f261b7ad48c
2020/11/03/[$LATEST]df9d6b71ef1e49789f4ebca64fc19270 2020-11-03T00:36:23.416000 REPORT RequestId: 3eb496cd-c663-4ae2-a717-8f261b7ad48c	Duration: 75.82 ms	Billed Duration: 100 ms	Memory Size: 128 MB	Max Memory Used: 65 MB
```
