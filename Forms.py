from wtforms import Form, StringField, RadioField, SearchField, TextAreaField, DecimalField, validators
from wtforms.fields import EmailField, DateField

class CreateReportForm(Form):
    reportName = StringField('Offender Username', [validators.DataRequired()])
    reportDesc = TextAreaField('Offence Committed', [validators.DataRequired()])