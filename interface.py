import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import wx

from main import *


class Form(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        self.grades = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Faculty']
        self.doLayout()

    def createControls(self):
        self.saveButton = wx.Button(self, label="Enroll With Facial Recognition")
        self.nameLabel = wx.StaticText(self, label="Your Name:")
        self.nameTextCtrl = wx.TextCtrl(self)
        self.referrerLabel = wx.StaticText(self,
                                           label="Your Grade:")
        self.referrerComboBox = wx.ComboBox(self, choices=self.grades)

    def create_controls2(self):
        self.startButton = wx.Button(self, label="Start Monitoring")

    def create_controls3(self):
        self.emailLabel = wx.StaticText(self, label="Your Email:")
        self.emailTextCtrl = wx.TextCtrl(self)
        self.dateLabel = wx.StaticText(self, label="Dates to Report:")
        self.dateTextCtrl = wx.TextCtrl(self)
        self.sendButton = wx.Button(self, label="Send Report")

    def create_controls4(self):
        self.passLabel = wx.StaticText(self, label="Your Password:")
        self.passTextCtrl = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.authButton = wx.Button(self, label="Authenticate")

    def bindEvents(self):
        for control, event, handler in \
                [(self.saveButton, wx.EVT_BUTTON, self.onSave),
                 (self.nameTextCtrl, wx.EVT_TEXT, self.onNameEntered),
                 (self.nameTextCtrl, wx.EVT_CHAR, self.onNameChanged),
                 (self.referrerComboBox, wx.EVT_COMBOBOX, self.onReferrerEntered),
                 (self.referrerComboBox, wx.EVT_TEXT, self.onReferrerEntered)]:
            control.Bind(event, handler)

    def bindEvents2(self):
        for control, event, handler in \
                [(self.startButton, wx.EVT_BUTTON, self.on_start)]:
            control.Bind(event, handler)

    def bindEvents3(self):
        for control, event, handler in \
                [(self.sendButton, wx.EVT_BUTTON, self.on_send),
                 (self.emailTextCtrl, wx.EVT_TEXT, self.onNameEntered),
                 (self.emailTextCtrl, wx.EVT_CHAR, self.onNameChanged)]:
            control.Bind(event, handler)

    def bindEvents4(self):
        for control, event, handler in \
                []:
            control.Bind(event, handler)

    def doLayout(self):
        ''' Layout the controls that were created by createControls().
            Form.doLayout() will raise a NotImplementedError because it
            is the responsibility of subclasses to layout the controls. '''
        raise NotImplementedError

        # Callback methods:

    def onColorchanged(self, event):
        self.__log('User wants color: %s' % self.colors[event.GetInt()])

    def onReferrerEntered(self, event):
        self.__log('User entered referrer: %s' % event.GetString())

    def onSave(self, event):
        confirmation_time = 50
        process_frequency = 2
        known_face_key_ids, known_face_labels, known_face_encodings, known_face_grade = get_data_from_db(
            face_encodings.find())
        name = self.nameTextCtrl.Value
        grade = self.referrerComboBox.Value
        print(name, grade)
        start_monitor(confirmation_time, process_frequency, make_480p, known_face_key_ids, known_face_labels,
                      known_face_encodings,
                      known_face_grade, True, register_pack=[name, grade])
        wx.MessageBox('User %s has been Successfully Added!' % name, 'Success', wx.OK | wx.ICON_INFORMATION)

    def onNameEntered(self, event):
        self.__log('User entered name: %s' % event.GetString())

    def onNameChanged(self, event):
        self.__log('User typed character: %d' % event.GetKeyCode())
        event.Skip()

    def onInsuranceChanged(self, event):
        self.__log('User wants insurance: %s' % bool(event.Checked()))

    # Helper method(s):

    def __log(self, message):
        ''' Private method to append a string to the logger text
            control. '''
        print('%s\n' % message)

    def on_start(self, event):
        confirmation_time = 50
        process_frequency = 2
        known_face_key_ids, known_face_labels, known_face_encodings, known_face_grade = get_data_from_db(
            face_encodings.find())
        start_monitor(confirmation_time, process_frequency, make_480p, known_face_key_ids, known_face_labels,
                      known_face_encodings,
                      known_face_grade)

    def on_send(self, event):
        mail_content = '''Hello,
        This is a test mail.
        In this mail we are sending some attachments.
        The mail is sent using Python SMTP library.
        Thank You
        '''
        # The mail addresses and password
        sender_address = 'michael1120040819@gmail.com'
        sender_pass = 'cjckzdlphkwiteds'
        receiver_address = self.emailTextCtrl.Value
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'A test mail sent by Python. It has an attachment.'
        # The subject line
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        attach_file_name = 'main.py'
        attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload((attach_file).read())
        encoders.encode_base64(payload)  # encode the attachment
        # add payload header with filename
        payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
        message.attach(payload)
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')
        wx.MessageBox('Successfully Sent!', 'Success', wx.OK | wx.ICON_INFORMATION)


class FormWithSizer(Form):
    def doLayout(self):
        self.createControls()
        self.bindEvents()
        ''' Layout the controls by means of sizers. '''

        # A horizontal BoxSizer will contain the GridSizer (on the left)
        # and the logger text control (on the right):
        boxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        # A GridSizer will contain the other controls:
        gridSizer = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [(self.nameLabel, noOptions),
                 (self.nameTextCtrl, expandOption),
                 (self.referrerLabel, noOptions),
                 (self.referrerComboBox, expandOption),
                 emptySpace,
                 (self.saveButton, dict(flag=wx.ALIGN_CENTER))]:
            gridSizer.Add(control, **options)

        for control, options in \
                [(gridSizer, dict(border=5, flag=wx.ALL))]:
            boxSizer.Add(control, **options)

        self.SetSizerAndFit(boxSizer)


class FormBegin(Form):
    def doLayout(self):
        self.create_controls2()
        self.bindEvents2()
        ''' Layout the controls by means of sizers. '''

        # A horizontal BoxSizer will contain the GridSizer (on the left)
        # and the logger text control (on the right):
        boxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        # A GridSizer will contain the other controls:
        gridSizer = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [(self.startButton, dict(flag=wx.ALIGN_CENTER))]:
            gridSizer.Add(control, **options)

        for control, options in \
                [(gridSizer, dict(border=5, flag=wx.ALL))]:
            boxSizer.Add(control, **options)

        self.SetSizerAndFit(boxSizer)


class FormReport(Form):
    def doLayout(self):
        self.create_controls3()
        self.bindEvents3()
        ''' Layout the controls by means of sizers. '''

        # A horizontal BoxSizer will contain the GridSizer (on the left)
        # and the logger text control (on the right):
        boxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        # A GridSizer will contain the other controls:
        gridSizer = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [(self.emailLabel, noOptions),
                 (self.emailTextCtrl, expandOption),
                 (self.dateLabel, noOptions),
                 (self.dateTextCtrl, expandOption),
                 emptySpace,
                 (self.sendButton, dict(flag=wx.ALIGN_CENTER))]:
            gridSizer.Add(control, **options)

        for control, options in \
                [(gridSizer, dict(border=5, flag=wx.ALL))]:
            boxSizer.Add(control, **options)

        self.SetSizerAndFit(boxSizer)


class FormAuth(Form):
    def doLayout(self):
        self.create_controls3()
        self.bindEvents3()
        ''' Layout the controls by means of sizers. '''

        # A horizontal BoxSizer will contain the GridSizer (on the left)
        # and the logger text control (on the right):
        boxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        # A GridSizer will contain the other controls:
        gridSizer = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [(self.emailLabel, noOptions),
                 (self.emailTextCtrl, expandOption),
                 (self.dateLabel, noOptions),
                 (self.dateTextCtrl, expandOption),
                 emptySpace,
                 (self.sendButton, dict(flag=wx.ALIGN_CENTER))]:
            gridSizer.Add(control, **options)

        for control, options in \
                [(gridSizer, dict(border=5, flag=wx.ALL))]:
            boxSizer.Add(control, **options)

        self.SetSizerAndFit(boxSizer)


class FrameWithForms(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(FrameWithForms, self).__init__(*args, **kwargs)
        notebook = wx.Notebook(self)
        form1 = FormBegin(notebook)
        form2 = FormWithSizer(notebook)
        form3 = FormReport(notebook)
        notebook.AddPage(form1, 'Monitor')
        notebook.AddPage(form2, 'Register')
        notebook.AddPage(form3, 'Report')
        # We just set the frame to the right size manually. This is feasible
        # for the frame since the frame contains just one component. If the
        # frame had contained more than one component, we would use sizers
        # of course, as demonstrated in the FormWithSizer class above.
        self.SetClientSize(notebook.GetBestSize())


class AuthFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(AuthFrame, self).__init__(*args, **kwargs)
        notebook = wx.Notebook(self)
        form1 = FormAuth(notebook)
        notebook.AddPage(form1, 'Authentication')
        # We just set the frame to the right size manually. This is feasible
        # for the frame since the frame contains just one component. If the
        # frame had contained more than one component, we would use sizers
        # of course, as demonstrated in the FormWithSizer class above.
        self.SetClientSize(notebook.GetBestSize())


# def collect_data():
# login_log.f


if __name__ == '__main__':
    app = wx.App(0)
    frame = FrameWithForms(None, title='Welcome Page')
    frame.Show()
    app.MainLoop()
