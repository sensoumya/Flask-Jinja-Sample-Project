from . import app
from .format import format
from flask_mongoalchemy import MongoAlchemy
from passlib.hash import pbkdf2_sha256 as sha256


app.config['MONGOALCHEMY_DATABASE'] = 'IntegrationUsers'
app.config['MONGOALCHEMY_CONNECTION_STRING'] = 'mongodb://localhost:27017'
app.config['SECRET_KEY'] = '691eca8c032a36a0ce029e5f587b76ff26dc8fab06a80ccb'
db = MongoAlchemy(app)


class UIUsers(db.Document):
    username = db.StringField()
    password = db.StringField()
    access = db.StringField()

    @classmethod
    def find_user(cls, username):
        return cls.query.filter(cls.username == username).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class Templates(db.Document):
    templatename = db.StringField()
    templatedata = db.ListField(db.StringField())

    @classmethod
    def fetchAttributes(cls, template_name):
        template = cls.query.filter(cls.templatename == template_name).first()
        return template.templatedata

    @classmethod
    def fetchTemplates(cls):
        return [item.templatename for item in cls.query.filter().all()]

    @classmethod
    def delTemplate(cls, template_name):
        template = cls.query.filter(cls.templatename == template_name).first()
        template.remove()

    @classmethod
    def findTemplate(cls, template_name):
        return cls.query.filter(cls.templatename == template_name).first()

    @classmethod
    def saveTemplate(cls, template_name, template_attribs):
        template = cls(templatename=template_name,
                       templatedata=template_attribs)
        template.save()


if len(UIUsers.query.filter().all()) < 1:
    user = UIUsers(username='admin@admin.com', password=UIUsers.generate_hash('admin'),
                   access='admin')
    user.save()

if len(Templates.query.filter().all()) < 1:
    for item in format.keys():
        Templates.saveTemplate(item, format[item])
