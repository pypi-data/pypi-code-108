from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,flash,jsonify, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, Form, form
from sqlalchemy.engine.base import Transaction
from sqlalchemy.sql.expression import label
from wtforms import HiddenField, StringField,FloatField ,SubmitField, DateField, IntegerField, DateTimeField, SelectField, RadioField
from wtforms.fields.core import BooleanField
from wtforms.validators import DataRequired, Optional
import requests
from db_init_file import db
from db_classes import FarmProduct, Mentor, Perspective,Customer,Employee, FarmObjective, FarmSensor, SensorForecast, Finance, \
    MentorComment,EmployeeStatus ,  EntityType, Farm, MeasureType, ObjectiveSensor, MeasureSensor, FarmMeasure, Stakeholder, User, MeasureStore, ObjectiveStore, SensorStore, \
    ObjectiveMeasure, Finance, ProductStore, ResourceType, ResourceStore, ResourceDatum, FarmResource, SensorResource, State, County, Stakeholder

import os
import flask_login
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import json
from user import UserUtils
import pandas as pd
import json
import plotly
import plotly.express as px

import jsonify

import logging
log = logging.getLogger()


# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


app = Flask(__name__)
db_password=os.environ["DB_PASS"]
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{db_password}@localhost:<port>/<db_name>"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = ''
db.app = app
db.init_app(app)
Bootstrap(app)
db.create_all()


# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return UserUtils.get(user_id, db.session)

class AddStakeholder(FlaskForm):
    listed_farm = db.session.query(Farm.farm_id).all()
    listed_resources = db.session.query(ResourceStore.resource_store_id).all()
    stakeholder_type = SelectField(label='Stakeholder type', choices=['Governing body', 'Donor', 'Investor', 'Partner company'], validators=[DataRequired()])
    stakeholder_name = StringField(label="Stakeholder name", validators=[DataRequired()])
    stakeholder_farm = SelectField(label="Farm", choices= [value for value, in listed_farm], validators=[DataRequired()])
    stakeholder_resources = SelectField(label='Resources', choices=[value for value, in listed_resources],validators=[DataRequired()])
    submit = SubmitField("Register a stakeholder")

class AddFarmer(FlaskForm):
    listed_farm = db.session.query(Farm.farm_id).all()
    farmer_name = StringField(label="Farmer name", validators=[DataRequired()])
    farmer_surname = StringField(label="Farmer surname", validators=[DataRequired()])  
    farm = SelectField(label='Select farm', choices= [value for value, in listed_farm], validators=[DataRequired()])
    submit = SubmitField('Register farmer')


class AddFarm(FlaskForm):
    entity_choices = db.session.query(EntityType.entity_type_id).all()
    entity_choices = [value for value, in entity_choices]
    city = StringField(label='City', validators=[DataRequired()])
    farm_type = SelectField(label="Type", choices=entity_choices, validators=[DataRequired()])
    longitude = StringField(label="longitude", validators=[DataRequired()])
    lattitude = StringField(label='lattitude', validators=[DataRequired()])
    size = IntegerField(label="Size in square meters", validators=[DataRequired()])
    submit = SubmitField(label='Add farm')


class AddSensor(FlaskForm):
    sensor_list = db.session.query(SensorStore.sensor_store_id).all()
    sensor_list = [value for value, in sensor_list]
    sensor = SelectField(label="Sensor", choices=sensor_list, validators=[DataRequired()])
    sensor_lower_bound = FloatField(label='Sensor lower bound value', validators=[DataRequired()])
    sensor_upper_bound = FloatField(label='Sensor upper bound value',validators=[Optional()])
    sensor_ideal_value = FloatField(label='Sensor ideal value', validators=[Optional()])
    submit = SubmitField('Submit')


class AddFarmMeasure(FlaskForm):

    measures = [value for value, in db.session.query(MeasureStore.measure_store_id).all()]
    measure = SelectField(label="Measure", choices=measures, validate_choice=[DataRequired()])
    submit = SubmitField('Submit')

class AddFarmObjective(FlaskForm):
    objective_types = [value for value, in db.session.query(Perspective.perspective_id).all()]
    objectives = [value for value, in db.session.query(ObjectiveStore.objective_id).all()]
    perspective = SelectField(label="Perspective/Objective type", choices=objective_types, validate_choice=[DataRequired()])
    objective = SelectField(label="Objective", choices=objectives, validate_choice=[DataRequired()])
    submit = SubmitField('Submit')



class AddResource(FlaskForm):
    ## Adds resource items to the resource store
    resource_types = [value for value, in db.session.query(ResourceType.resource_type).all()]
    farms = [value for value, in db.session.query(Farm.farm_id).all()]
    sources = [value for value, in db.session.query(ResourceType.source).all()]
    # sources = list(['Government', 'Donor', 'Natural', 'Self generated'])
    resource_type = SelectField(label='Resource type', choices=resource_types, validate_choice=[DataRequired()])
    resource_description = StringField(label='Resource description')
    farm = SelectField(label='Farm', choices=farms, default=None)
    source = SelectField(label='Source', choices=sources, validate_choice=[DataRequired()])
    capacity = FloatField(label='Source capacity (Rand value, kg, mm etc.)')
    can_split = BooleanField(label='Can this source be split?' )

    submit = SubmitField('Submit')


class AddFarmProduct(FlaskForm):

    products = [value for value, in db.session.query(ProductStore.product_id).all()]
    product = SelectField(label='Product', choices=products, validate_choice=[DataRequired()])
    submit = SubmitField("Submit")


class AddCustomer(FlaskForm):
    customer_name = StringField(label="Customer Name")

    submit = SubmitField('Submit')

class Transaction(FlaskForm):
    products = [value for value, in db.session.query(ProductStore.product_id).all()]
    products_bought = SelectField(label='Product', choices=products, validate_choice=[DataRequired()]) 


class AddFinance(FlaskForm):
    income = FloatField(label='Income', validators=[DataRequired()] )
    expenses = FloatField(label='Expenses', validators=[DataRequired()] )
    returns = FloatField(label='Returns', validators=[DataRequired()] )
    submit = SubmitField('Add Finances')

class LinkResource(FlaskForm):
    resources = [value for value, in db.session.query(ResourceStore.resource_store_id).all()]
    resource = SelectField(label='Resource', choices=resources, validate_choice=[DataRequired()])
    submit = SubmitField('Link Resource')

@app.route("/home", methods=['GET', 'POST'])
# @login_required
def home():
    all_farms = db.session.query(Farm).all()
    return render_template("home.html", farms=all_farms)



@app.route("/add_farmer", methods=['GET', 'POST'])
def add_farmer():
    new_farmer = AddFarmer()
    if request.method == "GET":
        farm_id = request.args['id']
        farm_employees = db.session.query(Employee).filter(Employee.farm_id==farm_id).all()

    if new_farmer.validate_on_submit():
        try:
            employee_id = int(max([value for value, in db.session.query(Employee.employee_id).all()])) + 1
        except:
            employee_id = 1
        farmer = Employee(employee_id=employee_id,
                        name=new_farmer.farmer_name.data,
                        surname=new_farmer.farmer_surname.data,
                        farm_id=new_farmer.farm.data)
        db.session.add(farmer)
        db.session.commit()
        
        return redirect(url_for('home'))
    return render_template("add_farmer.html", form=new_farmer, farmers=farm_employees, farm=farm_id)


@app.route("/add_stakeholder", methods=["GET","POST"])
def add_stakeholder():
    new_stakeholder = AddStakeholder()
    if request.method == "GET":
        stakeholders = db.session.query(Stakeholder.stakeholder_name, Stakeholder.stakeholder_type, Stakeholder.resource_store_id, Stakeholder.farm_id).all()
    
    if new_stakeholder.validate_on_submit():
        try:
            stakeholder_id = int(max([value for value, in db.session.query(Stakeholder.stakeholder_id).all()])) + 1
        except:
            stakeholder_id = 1
        
        stakeholder_resource_store_catalog_id = db.session.query(ResourceStore.resource_store_catalog_id).filter(ResourceStore.resource_store_id==new_stakeholder.stakeholder_resources.data)
        stakeholder = Stakeholder(stakeholder_id=stakeholder_id,
                                stakeholder_name=new_stakeholder.stakeholder_name.data,
                                resource_store_catalog_id=stakeholder_resource_store_catalog_id,
                                farm_id=new_stakeholder.stakeholder_farm.data,
                                resource_store_id = new_stakeholder.stakeholder_resources.data,
                                stakeholder_type=new_stakeholder.stakeholder_type.data)

        db.session.add(stakeholder)
        db.session.commit()
    
        return redirect(url_for('home'))
    # stakeholders = db.session.query(Stakeholder).all()
    
    return render_template("add_stakeholder.html", form=new_stakeholder, stakeholders=stakeholders)

@app.route("/add_resource", methods=["GET", "POST"])
#@login_required
def add_resource():
    new_resource = AddResource()
    resource_store_data = db.session.query(ResourceStore).all()
    try:
        resource_catalog_id = max([value for value, in db.session.query(ResourceStore.resource_store_catalog_id).all()]) + 1
    except:
        resource_catalog_id = 1
    
    if request.method == 'GET':
        resource_store_data = db.session.query(ResourceStore).all()

#          <th> {% for farm in farms %} <li> {{farm.farm_id}} </li> {% endfor %} </th>
    if new_resource.validate_on_submit():
        resource_store_data = db.session.query(ResourceStore).all()
        resource_catalog_id = resource_catalog_id
        resource_type = new_resource.resource_type.data
        resource_type_id = db.session.query(ResourceType.resource_type_id).filter(ResourceType.resource_type == resource_type)
        resource_description = new_resource.resource_description.data
        farm_id = new_resource.farm.data
        source = new_resource.source.data
        capacity = new_resource.capacity.data
        can_split = new_resource.can_split.data

        additional_resource = ResourceStore(
            resource_store_catalog_id = resource_catalog_id,
            resource_store_id = f"{resource_type.strip()}_{capacity}",
            resource_description = resource_description,
            farm_id = farm_id,
            resource_type_id = resource_type_id,
            resource_type = resource_type,
            source = source,
            capacity = capacity,
            can_split = can_split
        )
        db.session.add(additional_resource)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("add_resource.html", form=new_resource, resource_store_data=resource_store_data)


@app.route("/link_resource", methods=["GET", "POST"])
def link_resource():
    link_resource = LinkResource()

    all_resources = db.session.query(ResourceStore)
    if request.method == "GET":
        farm_id = request.args['id']
        
        resource_list_for_farm = db.session.query(FarmResource.resource_store_id, 
        ResourceStore.resource_description).filter_by(farm_id=farm_id).join(ResourceStore,
        ResourceStore.resource_store_catalog_id == FarmResource.resource_store_catalog_id).all()


    if link_resource.validate_on_submit():
        farm_id = request.args['id']
        try:
            farm_resource_relationship_id = max([value for value, in db.session.query(FarmResource.farm_resource_relationship_id).all()]) + 1
        except:
            farm_resource_relationship_id = 1
        
        resource_store_id = link_resource.resource.data
        resource_store_catalog_id = db.session.query(ResourceStore.resource_store_catalog_id).filter(ResourceStore.resource_store_id == resource_store_id)

        linked_resource = FarmResource(
            farm_resource_relationship_id = farm_resource_relationship_id,
            resource_store_catalog_id = resource_store_catalog_id,
            resource_store_id=resource_store_id,
            farm_id=farm_id
        )

        db.session.add(linked_resource)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("link_resource.html", all_resources=all_resources ,resources=resource_list_for_farm, form=link_resource, farm=farm_id)


@app.route("/add_sensor", methods=["GET", "POST"])
#@login_required
def add_sensor():
    new_sensor = AddSensor()
    try:
        sensor_catalog_id = max([value for value, in db.session.query(SensorStore.sensor_store_catalog_id).all()]) + 1
    except:
        sensor_catalog_id = 1

    if request.method == "GET" or 'POST':
        farm_id = request.args['id']
        sensor_list_for_farm = db.session.query(FarmSensor.sensor_store_id, 
        SensorStore.sensor_description).filter_by(farm_id=farm_id).join(SensorStore,
        SensorStore.sensor_store_catalog_id==FarmSensor.sensor_store_catalog_id).all()

    if new_sensor.validate_on_submit():
        # sensor_id = "{}_{}_{}".format(new_sensor.farm_id.data, new_sensor.sensor_type.data, sensor_catalog_id)
        farm_id = request.args['id']
        sensor_store_id = new_sensor.sensor.data
        sensor_store_catalog_id = db.session.query(SensorStore.sensor_store_catalog_id).filter_by(sensor_store_id=new_sensor.sensor.data).first()[0]
        sensor_lower_bound = new_sensor.sensor_lower_bound.data
        sensor_upper_bound = new_sensor.sensor_upper_bound.data
        sensor_ideal_value = new_sensor.sensor_ideal_value.data
        new_sensor = FarmSensor(sensor_store_catalog_id=sensor_store_catalog_id,
                            sensor_store_id=sensor_store_id,
                            farm_id=farm_id,
                            sensor_value_lower_bound=sensor_lower_bound,
                            sensor_value_upper_bound=sensor_upper_bound,
                            sensor_value_ideal=sensor_ideal_value,
                            create_time=datetime.now(timezone.utc)
                           )

        db.session.add(new_sensor)
        db.session.commit()
        # NOTE: You can use the redirect method from flask to redirect to another route
        # e.g. in this case to the home page after the form has been submitted.

        return redirect(url_for('home'))
    return render_template("add_sensor.html", sensors=sensor_list_for_farm, form=new_sensor, farm=farm_id)


@app.route("/add_farm", methods=["GET", "POST"])
#@login_required
def add_farm():
    new_farm = AddFarm()

    if new_farm.validate_on_submit():
        farm_id = "{}_{}_{}".format(new_farm.city.data, new_farm.longitude.data, new_farm.lattitude.data)
        farm_type = new_farm.farm_type.data
        longitude = new_farm.longitude.data
        lattitude = new_farm.lattitude.data
        size = new_farm.size.data
        entity_type = new_farm.farm_type.data
        new_farm = Farm(farm_id=farm_id,
                        farm_type=farm_type,
                        longitude=longitude,
                        lattitude=lattitude,
                        size=size,
                        entity_type_id=entity_type)

        db.session.add(new_farm)
        db.session.commit()
        # NOTE: You can use the redirect method from flask to redirect to another route
        # e.g. in this case to the home page after the form has been submitted.

        return redirect(url_for('home'))
    return render_template("add.html", form=new_farm)


@app.route("/low_info")
#@login_required
def low_info():
    return render_template("low_info.html")

@app.route("/high_info")
#@login_required
def high_info():
    return render_template("high_info.html")


@app.route("/add_measure", methods=["GET", "POST"])
#@login_required
def add_measure():

    new_measure = AddFarmMeasure()

    if request.method == "GET":
        farm_id = request.args['id']  
        farm_measures = db.session.query(FarmMeasure.measure_store_id,
        MeasureStore.measure_description).filter_by(farm_id=farm_id).join(MeasureStore,
     FarmMeasure.measure_store_catalog_id==MeasureStore.measure_store_catalog_id).all()

    if new_measure.validate_on_submit():
        try:
            farm_measure_catalog_id = max([value for value, in db.session.query(FarmMeasure.farm_measure_catalog_id).all()]) + 1
        except:
            farm_measure_catalog_id = 1
        measure_store_catalog_id = db.session.query(MeasureStore.measure_store_catalog_id).filter_by(measure_store_id=new_measure.measure.data).all()[0][0]
        farm_id = request.args['id']
        farm_measures = db.session.query(FarmMeasure).filter_by(farm_id=farm_id).join(MeasureStore, FarmMeasure.measure_store_catalog_id==MeasureStore.measure_store_catalog_id).all()

        measure_store_id = new_measure.measure.data 
        new_measure = FarmMeasure(farm_measure_catalog_id=farm_measure_catalog_id,
                                    measure_store_catalog_id=measure_store_catalog_id,
                                    farm_id=farm_id,
                                    measure_store_id=measure_store_id
                                    )
        db.session.add(new_measure)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_measure.html', farm=farm_id, measures=farm_measures, form=new_measure)
#
#
@app.route("/add_objective", methods=['GET', 'POST'])
#@login_required
def add_objective():

    new_objective = AddFarmObjective()

    if request.method == "GET":
        farm_id = request.args['id']
        objectives = db.session.query(FarmObjective.objective_id, ObjectiveStore.objective_description, ObjectiveStore.perspective_id).join(ObjectiveStore, ObjectiveStore.objective_id==FarmObjective.objective_id).filter(FarmObjective.farm_id==farm_id).all()
        
    if new_objective.validate_on_submit():

        try:
            farm_objective_catalog_id = max([value for value, in db.session.query(FarmObjective.farm_objective_catalog_id).all()]) + 1
        except Exception as e:
            farm_objective_catalog_id = 1
        
        new_objective.objective.choices = [value for value, in db.session.query(ObjectiveStore.objective_id).filter(ObjectiveStore.perspective_id==new_objective.perspective.data)]
        farm_id = request.args['id']
        # farm_id = db.session.query(Farm.farm_id).filter_by(farm_id=farm_id).all()[0][0]
        objectives = db.session.query(FarmObjective.objective_id, ObjectiveStore.objective_description, ObjectiveStore.perspective_id).join(ObjectiveStore, ObjectiveStore.objective_id==FarmObjective.objective_id).filter(FarmObjective==farm_id).all()
        new_objective = FarmObjective(farm_objective_catalog_id=farm_objective_catalog_id,
                                    objective_id=new_objective.objective.data,
                                    farm_id=farm_id)
        db.session.add(new_objective)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_objective.html', farm=farm_id, objectives=objectives, form=new_objective)


@app.route("/farm_overview",methods=['GET', 'POST'])
def farm_overview():
    if request.method == "GET":
        farm_id = request.args['id']
        farm_measures = db.session.query(FarmMeasure).filter(FarmMeasure.farm_id==farm_id).all()
        farm_sensors = db.session.query(FarmSensor).filter(FarmSensor.farm_id==farm_id).all()
        farm_objectives = db.session.query(FarmObjective).filter(FarmObjective.farm_id==farm_id).all()
        farm_products = db.session.query(FarmProduct).filter(FarmProduct.farm_id==farm_id).all()
        farm_resources = db.session.query(FarmResource).filter(FarmResource.farm_id==farm_id).all()
        farmers = db.session.query(Employee).filter(Employee.farm_id==farm_id).all()
    return render_template('overview.html',
                                            farm_id=farm_id,
                                            farm_measures=farm_measures,
                                            farm_sensors=farm_sensors,
                                            farm_objectives=farm_objectives,
                                            farm_products=farm_products,
                                            farm_resources=farm_resources,
                                            farmers=farmers)
    # return redirect(url_for("home"))



@app.route("/add_products", methods=['GET', 'POST'])
def add_products():
    new_product = AddFarmProduct()

    if request.method == "GET":
        farm_id = request.args['id']
        products = db.session.query(FarmProduct.product_id, ProductStore.product_description).join(ProductStore, ProductStore.product_id == FarmProduct.product_id).filter(FarmProduct.farm_id==farm_id).all()

    if new_product.validate_on_submit():
        try:
            farm_product_catalog_id = max([value for value, in db.session.query(FarmProduct.farm_product_catalog_id).all()]) + 1
        except Exception as e:
            farm_product_catalog_id = 1

        farm_id = request.args['id']
        products = db.session.query(FarmProduct.product_id, ProductStore.product_description).join(ProductStore, ProductStore.product_id == FarmProduct.product_id).filter(FarmProduct.farm_id==farm_id).all()

        additional_product = FarmProduct(farm_product_catalog_id=farm_product_catalog_id,
                                    farm_id=farm_id,
                                    product_id=new_product.product.data)

        db.session.add(additional_product)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_product.html', farm=farm_id, products=products, form=new_product)
###
### The customer view table where we can track the various customers in the database
###
@app.route("/customer")




###
### The farm finance view where the farmers can track their finances
###
@app.route("/finances", methods=['GET', 'POST'])
def finances():
    finance_form = AddFinance()
    
    if request.method == "GET" or "POST":
        farm_id = request.args['id']
        income_transactions=db.session.query(Finance).filter(Finance.farm_id==farm_id).all()
        expense_transactions=db.session.query(Finance).filter(Finance.farm_id==farm_id).all()
        returns=db.session.query(Finance).filter(Finance.farm_id==farm_id).all()
        historical_dates=db.session.query(Finance).filter(Finance.farm_id==farm_id).all()
        expected_revenue = db.session.query(Finance).filter(Finance.farm_id==farm_id).all()
    if finance_form.validate_on_submit():

        try:
            tran_id = max([value for value, in db.session.query(Finance.tran_id).all()]) + 1
        except:
            tran_id = 1
        
        farm_id = request.args['id']
        income = finance_form.income.data
        expense = finance_form.expenses.data
        returns = finance_form.returns.data
        expected_revenue = income - expense- returns
        new_transaction = Finance(
                                    tran_id=tran_id,
                                    farm_id=farm_id,
                                    income=income,
                                    expense=expense,
                                    returns=returns,
                                    expected_revenue=expected_revenue
                                    )
        db.session.add(new_transaction)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('finances.html',
                                            farm_id=farm_id,
                                            income_transactions=income_transactions,
                                            expense_transactions=expense_transactions,
                                            historical_dates=historical_dates,
                                            returns=returns,
                                            expected_revenue=expected_revenue,
                                            form=finance_form)


###
### Strategic decisions
###

@app.route("/strategic_decisions", methods=['GET', 'POST'])
def strategic_decisions():

    render_template('strategic_decisions.html')


###
### Strategic decisions
###



    
###
### The mentor view where metnors can sign in, view farm states make comments/blog
###

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return '<a class ="btn btn-warning btn-lg" href="/login">Google Login</a>'


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
        id=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.

    if not UserUtils.get(unique_id, db.session):
        UserUtils.create(unique_id, users_name, users_email, picture, db.session)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
#@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(ssl_context='adhoc',debug=True, host='127.0.0.1', port=int(os.environ.get("PORT", 5000)))
