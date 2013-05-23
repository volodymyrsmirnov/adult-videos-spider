#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Masturbator interface
Used for scrapping the data from the porn sites
"""

import requests

class MasturbatorException(Exception):
	"""
	Masturbator exception class
	"""
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

class Masturbator(object):
	"""
	Basic masturbator class
	"""

	def first_or_value(self, fromlist, value=None):
		"""
		Return first element of list or value if not found
		"""
		return (fromlist + [value])[0]

	def request(self, url, method="GET", headers={}, data={}, timeout=5, return_binary=False):
		"""
		Make a http request
		"""
		r = None

		headers["User-Agent"] = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

		try:
			if method == "GET":
				r = requests.get(url, data=data, headers=headers, timeout=timeout, allow_redirects=True)

			elif method == "POST":
				r = requests.post(url, data=data, headers=headers, timeout=timeout, allow_redirects=True)

		except requests.exceptions.ConnectionError:
			raise MasturbatorException("connection error")

		if r == None:
			raise MasturbatorException("unsupported request method")

		if not r.status_code == requests.codes.ok:
			raise MasturbatorException("non 200 response code received")

		if return_binary:
			return r.content
		else:
			return r.text

	def fap(self):
		raise MasturbatorException("not implemented in current class")