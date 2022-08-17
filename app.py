from flask import Flask, render_template, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, DateField, SelectMultipleField
from werkzeug.utils import secure_filename
import os
from io import StringIO
from wtforms.validators import InputRequired, DataRequired
from babel.numbers import format_decimal

import jinja2

import plotly
import json

import pandas as pd
import numpy as np

import utils
import plots
import preds
import dataframes


# Decimal format for Jinja2
def FormatDecimal(value):
    return format_decimal(float(value), format='#,##0')

jinja2.filters.FILTERS['FormatDecimal'] = FormatDecimal





app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'


class UploadFile(FlaskForm):
    upload = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload/', methods=['GET',"POST"])
def upload():
    form = UploadFile()
    if form.validate_on_submit():
        # Save file to the upload folder
        file = form.upload.data
        if utils.allowed_file(file.filename):
            file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                app.config['UPLOAD_FOLDER'],
                secure_filename(file.filename))
            file.save(file_path)
            if (len(pd.read_csv(file_path).columns) == len(utils.columns))\
            and (pd.read_csv(file_path).columns == utils.columns).mean():
                #Upload file to S3
                utils.client.upload_file(file_path, utils.bucket, file.filename)
                # Delete file from upload folder
                os.remove(file_path)
                flash('The file has been uploaded')
                return render_template('upload.html', form=form)
            else:
                # Delete file from upload folder
                os.remove(file_path)
                flash('Please check the column names')
                return render_template('upload.html', form=form)
            
        else:
            flash('Make sure you upload file in csv or xlsx format')
            return render_template('upload.html', form=form)
    return render_template('upload.html', form=form)

class FilterForm(FlaskForm):

    start_date = DateField('Start Date')
    end_date = DateField('End Date')
    company_name = SelectMultipleField('Company Name',
        validate_choice=False)
    studio_name = SelectMultipleField('Studio', choices=[],
        validate_choice=False)
    product_name = SelectMultipleField('Product', choices=[],
        validate_choice=False)
    submit = SubmitField('Submit')

 








###########################Profit Page###############################################################




@app.route('/profit/', methods=['GET',"POST"])
def profit():
    form = FilterForm()
    form.company_name.choices=['All'] + utils.unique_value('Company')
    form.studio_name.choices=['All']+ utils.unique_value('Studio')
    form.product_name.choices=['All']+ utils.unique_value('Project')
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        company_name = form.company_name.data
        studio_name = form.studio_name.data
        product_name = form.product_name.data
        if company_name[0] == 'All' and studio_name[0] == 'All' and product_name[0] == 'All':

            df = dataframes.df_main(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'")
            df_project = dataframes.df_project(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'")
            df_table = dataframes.df_table(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'")
            df_preds = dataframes.df_preds()

            fig = plots.profit_by_month_bar(df)
            graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            fig2 = plots.cumline(df)
            graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            fig3 = plots.bar_project(df_project)
            graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            fig4 = plots.predictions(df_preds)
            graph4=json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('profit.html', form=form, graph=graph, graph2=graph2, graph3=graph3, 
                    graph4=graph4, df=df_table)

        if company_name[0] != 'All' and studio_name[0] == 'All' and product_name[0] == 'All':

            df = dataframes.df_main(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name)
            df_project = dataframes.df_project(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name)
            df_table = dataframes.df_table(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name)
            df_preds = dataframes.df_preds(company_name=company_name)
            
            fig = plots.profit_by_month_bar(df)
            graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            fig2 = plots.cumline(df)
            graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            fig3 = plots.bar_project(df_project)
            graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            fig4 = plots.predictions(df_preds)
            graph4=json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('profit.html', form=form, graph=graph, graph2=graph2, graph3=graph3, 
                    graph4=graph4, df=df_table)
           
        if company_name[0] == 'All' and studio_name[0] != 'All' and product_name[0] == 'All':

            df = dataframes.df_main(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", studio_name=studio_name)
            df_project = dataframes.df_project(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", studio_name=studio_name)
            df_table = dataframes.df_table(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", studio_name=studio_name)
            df_preds = dataframes.df_preds(studio_name=studio_name)
            
            fig = plots.profit_by_month_bar(df)
            graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            fig2 = plots.cumline(df)
            graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            fig3 = plots.bar_project(df_project)
            graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            fig4 = plots.predictions(df_preds)
            graph4=json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('profit.html', form=form, graph=graph, graph2=graph2, graph3=graph3, 
                    graph4=graph4, df=df_table)

        if company_name[0] == 'All' and studio_name[0] == 'All' and product_name[0] != 'All':

            df = dataframes.df_main(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", product_name=product_name)
            df_project = dataframes.df_project(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", product_name=product_name)
            df_table = dataframes.df_table(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", product_name=product_name)
            df_preds = dataframes.df_preds(product_name=product_name)
            
            fig = plots.profit_by_month_bar(df)
            graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            fig2 = plots.cumline(df)
            graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            fig3 = plots.bar_project(df_project)
            graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            fig4 = plots.predictions(df_preds)
            graph4=json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('profit.html', form=form, graph=graph, graph2=graph2, graph3=graph3, 
                    graph4=graph4, df=df_table)

        if company_name[0] != 'All' and studio_name[0] != 'All' and product_name[0] == 'All':

            df = dataframes.df_main(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name, studio_name=studio_name)
            df_project = dataframes.df_project(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name, studio_name=studio_name)
            df_table = dataframes.df_table(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name, studio_name=studio_name)
            df_preds = dataframes.df_preds(company_name=company_name, studio_name=studio_name)
            
            fig = plots.profit_by_month_bar(df)
            graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            fig2 = plots.cumline(df)
            graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            fig3 = plots.bar_project(df_project)
            graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            fig4 = plots.predictions(df_preds)
            graph4=json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('profit.html', form=form, graph=graph, graph2=graph2, graph3=graph3, 
                    graph4=graph4, df=df_table)


        if company_name[0] != 'All' and studio_name[0] == 'All' and product_name[0] != 'All':

            df = dataframes.df_main(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name, product_name=product_name)
            df_project = dataframes.df_project(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name, product_name=product_name)
            df_table = dataframes.df_table(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name, product_name=product_name)
            df_preds = dataframes.df_preds(company_name=company_name, product_name=product_name)
            
            fig = plots.profit_by_month_bar(df)
            graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            fig2 = plots.cumline(df)
            graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            fig3 = plots.bar_project(df_project)
            graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            fig4 = plots.predictions(df_preds)
            graph4=json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('profit.html', form=form, graph=graph, graph2=graph2, graph3=graph3, 
                    graph4=graph4, df=df_table)


        if company_name[0] == 'All' and studio_name[0] != 'All' and product_name[0] != 'All':

            df = dataframes.df_main(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", studio_name=studio_name, product_name=product_name)
            df_project = dataframes.df_project(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", studio_name=studio_name, product_name=product_name)
            df_table = dataframes.df_table(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", studio_name=studio_name, product_name=product_name)
            df_preds = dataframes.df_preds(studio_name=studio_name, product_name=product_name)
            
            fig = plots.profit_by_month_bar(df)
            graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            fig2 = plots.cumline(df)
            graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            fig3 = plots.bar_project(df_project)
            graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            fig4 = plots.predictions(df_preds)
            graph4=json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('profit.html', form=form, graph=graph, graph2=graph2, graph3=graph3, 
                    graph4=graph4, df=df_table)

        if company_name[0] != 'All' and studio_name[0] != 'All' and product_name[0] != 'All':

            df = dataframes.df_main(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name, studio_name=studio_name, product_name=product_name)
            df_project = dataframes.df_project(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name, studio_name=studio_name, product_name=product_name)
            df_table = dataframes.df_table(start_date="'"+str(start_date)+"'", end_date="'"+str(end_date)+"'", company_name=company_name, studio_name=studio_name, product_name=product_name)
            df_preds = dataframes.df_preds(company_name=company_name, studio_name=studio_name, product_name=product_name)

            fig = plots.profit_by_month_bar(df)
            graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            fig2 = plots.cumline(df)
            graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            fig3 = plots.bar_project(df_project)
            graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            fig4 = plots.predictions(df_preds)
            graph4=json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('profit.html', form=form, graph=graph, graph2=graph2, graph3=graph3, 
                    graph4=graph4, df=df_table)

    df = dataframes.df_main_nf()
    df_project = dataframes.df_project_nf()
    df_table = dataframes.df_table_nf()
    df_preds = dataframes.df_preds()
     
    fig = plots.profit_by_month_bar(df)
    graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig2 = plots.cumline(df)
    graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    fig3 = plots.bar_project(df_project)
    graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    fig4 = plots.predictions(df_preds)
    graph4=json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)

    
    return render_template('profit.html', form=form, graph=graph, graph2=graph2, graph3=graph3, 
        graph4=graph4, df=df_table)





















class PredictionsForm(FlaskForm):
    submit = SubmitField('Make Predictions')


@app.route('/predictions/', methods=['GET',"POST"])
def predictions():
    form = PredictionsForm()
    if form.validate_on_submit():
        ######for predictions#######
        df_preds = preds.display_all_predictions(utils.read_file_s3(utils.bucket)).reset_index()
        csv_buf = StringIO()
        df_preds.to_csv(csv_buf, header=True, index=False)
        csv_buf.seek(0)
        utils.client.put_object(Bucket=utils.bucket2, Body=csv_buf.getvalue(), Key='preds.csv')
        return render_template('predictions.html', form=form)
    return render_template('predictions.html', form=form)










### TODO
# https://www.youtube.com/watch?v=I2dJuNwlIH0
# Dynamic Select Fields
@app.route('/studio/<company>')
def studio(company):
    df = utils.read_file_s3()
    studios = list(df[df['Company']==company]['Studio'].unique())
    studioArray = list()
    for studio in studios:
        studioObj = {}
        studioObj['id'] = studio
        studioObj['name'] = studio
        studioArray.append(studioObj)
    return jsonify( {'studios': studioArray})



