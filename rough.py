import smtplib

server = smtplib.SMTP('smtp.gmail.com',587)

server.starttls()

server.login("backenddeveloperformyprojectus@gmail.com","jvim gusx hbsy jszz")

server.sendmail("backenddeveloperformyprojectus@gmail.com","biswayanmal@outlook.com","DONE")

print("Successful send")