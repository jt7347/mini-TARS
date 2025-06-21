import subprocess
import base64
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'miniTARSAI@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD = 'kljyooyoalziwpsx'  #change this to match your gmail password

class TARS_Camera:
    def __init__(self):
        self.timeout = 1000
        self.filename = "image.jpg"

    def take_photo(self):
        # Run the libcamera-still command to capture an image
        try:
            subprocess.run(["libcamera-still", "-o", self.filename, "--width", "500", "--height", "500", "--timeout", "1000"], check=True)
            ret = self.encode_image(self.filename)
            return ret
        except subprocess.CalledProcessError:
            print("Error: Failed to capture image.")
            # None return
            return
    
    def encode_image(self, filename):
        '''Separate the take photo and encode image to allow
        usage of encoding function w/o needing to take a photo.'''
        with open(filename, "rb") as img_file:
            base64_string = base64.b64encode(img_file.read()).decode('utf-8')
            return base64_string
        
    def send_mail(self):
        #Create Headers
        recipient = GMAIL_USERNAME
        emailData = MIMEMultipart()
        emailData['Subject'] = "Data Transmission"
        emailData['To'] = recipient
        emailData['From'] = GMAIL_USERNAME

        #Attach our text data
        emailData.attach(MIMEText("This photo was taken at: " + time.ctime()))

        #Create our Image Data from the defined image
        imageData = MIMEImage(open(self.filename, 'rb').read(), 'jpg')
        imageData.add_header('Content-Disposition', 'attachment; filename=' + self.filename)
        emailData.attach(imageData)

        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, emailData.as_string())
        session.quit


# Main function to interact with the user
def main():
    TARS = TARS_Camera()
    ret = TARS.take_photo()
    TARS.send_mail()

if __name__ == "__main__":
    main()
