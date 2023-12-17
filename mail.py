import os


 recipient = "jacksonmuta123@gmail.com"


 email_body = """
 <!DOCTYPE html>
 <html>
 <head>
   <title>Email Confirmation</title>
 </head>
 <body style ="font-size: 20px;">
   <p>You have received this email because it was used to create an account.If
 this wasn't you please ignore it.

<br>
{}
</p>


 </p>
 </body>
 </html>
 """.format(code)

email_command = f'mail -a "Content-Type: text/html" -s "Appreciation" {recipient} <<EOF' 
full_email = email_command + email_body
os.system(full_email)
