# Dovecot clouldformatoin demo.<br/>
#############################################<br/><br/>

#AWS Structure:<br/>
PostFix + Dovecot Direct + Dovecot Backend (with RDS user authentication)<br/><br/>

Use EFS to store & share user mail data across Postfix and Director Backends.<br/><br/>
It can update dovecot director configure and restart dovecot server automatically once the director cluster data update.<br/>


Sample CMD:<br/>
aws cloudformation create-stack --stack-name {StackName} --template-body file:///Users/eason/..../cf_template.json  --parameters ParameterKey=KeyName,ParameterValue={RSA_KEY_FILE} --region us-west-2 --capabilities CAPABILITY_IAM<br/>
aws cloudformation delete-stack --stack-name {StackName}<br/><br/>

NOTE:
For V1.3 ONLY! After enviroment set, call "cd /mnt/post_dovecot_demo/ && python director_monitor.py initial" on postfix ec2 to boot whole dovecot cluster!

#############################################<br/>
