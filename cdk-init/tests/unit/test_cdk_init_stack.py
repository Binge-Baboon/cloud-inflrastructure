import aws_cdk as core
import aws_cdk.assertions as assertions
from cdk_init.cdk_init_stack import CdkInitStack


def test_sqs_queue_created():
    app = core.App()
    stack = CdkInitStack(app, "cdk-init")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })


def test_sns_topic_created():
    app = core.App()
    stack = CdkInitStack(app, "cdk-init")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::SNS::Topic", 1)
