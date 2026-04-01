from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class TransactionForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    transaction_type = SelectField('Type', choices=[('IN','Stock IN'),('OUT','Stock OUT'),('ADJUSTMENT','Adjustment')], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    note = TextAreaField('Note', validators=[Optional()])
    submit = SubmitField('Record Transaction')
