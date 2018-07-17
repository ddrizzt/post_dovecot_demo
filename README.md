# Dovecot clouldformatoin demo.<br/>
#############################################<br/><br/>

#AWS Structure:<br/>
PostFix + Dovecot Direct + Dovecot Backend (with RDS user authentication)<br/><br/>

Use EFS to store & share user mail data across Postfix and Director Backends.<br/><br/>

Sample CMD:<br/>
aws cloudformation create-stack --stack-name {StackName} --template-body file:///Users/eason/..../cf_template.json  --parameters ParameterKey=KeyName,ParameterValue={RSA_KEY_FILE} --region us-west-2 --capabilities CAPABILITY_IAM<br/>
aws cloudformation delete-stack --stack-name {StackName}<br/><br/>

#############################################<br/>
