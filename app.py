from flask import Flask, render_template, request
import logfire
import json

from flask_googlemaps import get_coordinates, GoogleMaps

from wtforms import Form, BooleanField, StringField, validators

from functions import agent

# configure logfire


app = Flask(__name__)

app.config.from_file("config.json", load= json.load)
logfire.configure(token=app.config["TOKEN"])
logfire.instrument_pydantic_ai()
GoogleMaps(app, key=app.config["GOOGLEMAPS_KEY"])

class GeolocForm(Form):
    adress = StringField("Dirección Completa", [validators.Length(min=1, max=200)])
    submit = BooleanField("Submit")


@app.route("/", methods=["GET", "POST"])
def  geoloc():
    form = GeolocForm(request.form)
    if request.method == "POST" and form.validate():
        adress = form.adress.data
        coordinates = get_coordinates(address_text=adress, API_KEY=app.config["GOOGLEMAPS_KEY"])
        if coordinates:
            lat, lng = coordinates["lat"], coordinates["lng"]
            answer = agent.run_sync(f"Las coordenadas del usuario son: ({lat}, {lng}), obténme los perfiles de plantas prospectivas para esta ubicación.")
            profiles = answer.output
            if not profiles:
                profiles = [{"name": "No se encontraron perfiles para esta dirección."}]
        else:
            profiles = [{"name": "No se pudieron obtener las coordenadas."}]
        return render_template("coordinates.html", profiles=profiles)
    return render_template("index.html", form=form)