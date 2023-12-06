# cognito-cdk-stack

Infrastructure containing a Cognito User Pool, and an application integration client. This is to support / demo the script in the parent directory of this project.

## Deployment 

### Pre-requisites 

* Since this is a [TypeScript](https://www.typescriptlang.org/) CDK project, you should have [npm](https://www.npmjs.com/) installed (which is the package manager for TypeScript/JavaScript).
    * You can find installation instructions for npm [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

* Additionally, it would be required for your to have [AWS CLI](https://aws.amazon.com/cli/) installed on your computer.
    *  `pip install awscli`. This means need to have python installed on your computer (if it is not already installed.)
    * You need to also configure and authenticate your AWS CLI to be able to interact with AWS programmatically. Detailed instructions of how you could do that are provided [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)

### Instructions

#### Install dependencies (if not done already)

```
npm install
```

#### Bootstrap (if not done already)

```
npx cdk bootstrap 
```

#### Deploy the "CognitoCdkStack"

```
npx cdk deploy CognitoCdkStack
```

Optionally you can specify a `--profile` argument if you are not deploying to the default AWS profile. Alternatively you can switch your default aws profile by setting the `AWS_PROFILE` environment variable.


## Generic CDK commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template
