from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=150)])
    sku = StringField('SKU', validators=[DataRequired(), Length(max=50)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Initial Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField('Unit', validators=[DataRequired(), Length(max=30)])
    minimum_threshold = IntegerField('Minimum Threshold', validators=[DataRequired(), NumberRange(min=0)])
    maximum_capacity = IntegerField('Maximum Capacity', validators=[DataRequired(), NumberRange(min=1)])
    purchase_price = DecimalField('Purchase Price', validators=[Optional()], places=2)
    selling_price = DecimalField('Selling Price', validators=[Optional()], places=2)
    supplier = StringField('Supplier', validators=[Optional(), Length(max=150)])
    submit = SubmitField('Save Product')
