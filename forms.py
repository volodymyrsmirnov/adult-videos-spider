#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
MyLust forms
"""

from flask.ext.babel import lazy_gettext
from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField, validators, ValidationError, TextAreaField, SelectField, FloatField

from flask.ext.wtf.html5 import EmailField, URLField

contact_topics = [
	(0, lazy_gettext("General questions")),
	(1, lazy_gettext("Partnership and advertising offers")),
	(2, lazy_gettext("Report abusive content")),
	(3, lazy_gettext("Report copyright infringement")),
]
	
class ContactForm(Form):
	name = TextField(lazy_gettext("Your name"), [
		validators.Required(message=lazy_gettext("This field is required.")),
		validators.Length(max=128)
	])

	email = EmailField(lazy_gettext("Reply back to email"), [
		validators.Email(message=lazy_gettext("This should be a valid email")),
		validators.Required(message=lazy_gettext("This field is required."))
	])

	topic = SelectField(lazy_gettext("Topic"), choices=contact_topics, coerce=int)

	message = TextAreaField(lazy_gettext("Message"), [
		validators.Required(message=lazy_gettext("This field is required.")),
	])

	captcha = RecaptchaField(lazy_gettext("Please enter the CAPTCHA"))