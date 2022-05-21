import json

import pandas as pd
import plotly
import plotly.graph_objs as go
import requests
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from pymongo import MongoClient

from website.models import IPAddresses

views = Blueprint('views', __name__)

client = MongoClient('localhost', 27017)
database = client['test_location_database']
col_table = database['i_p_addresses']


def fetch_ip_data(ip_req):
    response = requests.get(ip_req)

    data = json.loads(response.text)

    filter_list = ['ip', 'continent', 'country', 'country_code', 'region', 'region_code', 'city']

    filtered_data = dict(filter(lambda e: e[0] in filter_list, data.items()))

    df = pd.DataFrame.from_dict(filtered_data, orient='index').T

    return df, filtered_data


def table_data_filter():
    table_data = IPAddresses.objects.order_by('+search_frequency')

    ip, continent, country, country_code, region, region_code, city, search_frequency, u_email = [], [], [], [], [], [], [], [], []
    ip_dictionary = {}
    for rec in table_data:
        ip.append(rec.ip)
        continent.append(rec.continent)
        country.append(rec.country)
        country_code.append(rec.country_code)
        region.append(rec.region)
        region_code.append(rec.region_code)
        city.append(rec.city)
        search_frequency.append(rec.search_frequency)
        u_email.append(rec.user_email)
    ip_dictionary['ip'], ip_dictionary['continent'], ip_dictionary['country'], ip_dictionary['country_code'], \
    ip_dictionary['region'], ip_dictionary['region_code'], ip_dictionary['city'], ip_dictionary[
        'search_frequency'], ip_dictionary[
        'user_email'] = ip, continent, country, country_code, region, region_code, city, search_frequency, u_email

    table_dataframe = pd.DataFrame.from_dict(ip_dictionary)
    table_dataframe = table_dataframe.loc[table_dataframe['user_email'] == str(current_user.email)]
    table_dataframe = table_dataframe[[
        'ip', 'continent', 'country', 'country_code', 'region', 'region_code', 'city', 'search_frequency']]
    table_dataframe = table_dataframe.sort_values('search_frequency', ascending=False)
    return table_dataframe


@views.route('/', methods=['GET', 'POST'])
@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        table_dataframe = table_data_filter()
        try:
            most_searched_country = table_dataframe.groupby('country')
            m_s_c = most_searched_country['search_frequency'].max()
            msc = m_s_c.to_frame().reset_index()
            actual_msc = msc.iloc[0]['country']
            return render_template("home.html", user=current_user,
                                   pop_columns=table_dataframe.columns.values,
                                   pop_rows=list(table_dataframe.values.tolist()), zip=zip,
                                   most_searched=actual_msc)
        except:
            pass
    if request.method == 'POST':
        ip_address = request.form.get('ip')
        if ip_address == None:
            pass
        else:
            ip_address = ip_address.strip()
            domain = 'http://ipwho.is/'
            ip_req = ''.join([domain, ip_address])

            df = fetch_ip_data(ip_req=ip_req)[0]
            filtered_data = fetch_ip_data(ip_req=ip_req)[1]

            table_dataframe = table_data_filter()

            check_ip = IPAddresses.objects(ip=ip_address).first()
            email_data = IPAddresses.objects.order_by('user_email')
            ips, emails = [], []

            for rec in email_data:
                ips.append(rec.ip)
                emails.append(rec.user_email)
            data_pairs = dict(zip(ips, emails))
            print(data_pairs)
            key, value = ip_address, current_user.email
            result = key in data_pairs and value == data_pairs[key]
            if result:
                IPAddresses.objects(ip=ip_address).modify(upsert=True, new=True, inc__search_frequency=1)
            else:
                try:
                    IPAddresses(ip=filtered_data['ip'], continent=filtered_data['continent'],
                                country=filtered_data['country'], country_code=filtered_data['country_code'],
                                region=filtered_data['region'], region_code=filtered_data['region_code'],
                                city=filtered_data['city'], search_frequency=1, user_email=current_user.email).save()
                    print("IP INSERTED SUCCESSFULLY IN DB")
                except KeyError:
                    print("API request returned no data")
                    pass

            return render_template("home.html", user=current_user, column_names=df.columns.values,
                                   row_data=list(df.values.tolist()), link_column="Patient ID",
                                   pop_columns=table_dataframe.columns.values,
                                   pop_rows=list(table_dataframe.values.tolist()), zip=zip,
                                   search="Search Results")

    return render_template("home.html", user=current_user)


def create_pie_chart():
    email_data = IPAddresses.objects.order_by('user_email')

    labels, values = [], []

    for rec in email_data:
        labels.append(rec.country)
        values.append(rec.search_frequency)
    data = [go.Pie(labels=labels, values=values)]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def create_heatmap():
    # email_data = IPAddresses.objects.order_by('user_email')

    data = table_data_filter()
    grp = data.groupby(['region', 'country'])['region_code'].count()
    grp_data = grp.to_frame().reset_index()
    region = grp_data['region'].to_list()
    country = grp_data['country'].to_list()
    code = list(zip(region, country))
    reg_code_count = grp_data['region_code'].to_list()

    data = [go.Heatmap(z=[reg_code_count], x=region, text=[country])]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@views.route('/visualizations', methods=['GET', 'POST'])
@login_required
def visualizations():
    pie = create_pie_chart()
    heatmap = create_heatmap()
    return render_template('visualizations.html', user=current_user, plot=pie, heatmap_plot=heatmap)
