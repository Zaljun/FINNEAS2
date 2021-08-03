from flask import Flask, redirect, url_for, render_template, request
import os
import controller

app = Flask(__name__)

picFolder = os.path.join('/static')

app.config['UPLOAD_FOLDER'] = picFolder

@app.route("/", methods=['GET', 'POST'])
def home():
    FinPic = os.path.join(app.config['UPLOAD_FOLDER'], 'FINNEAS.png')
    homepic = os.path.join(app.config['UPLOAD_FOLDER'], 'finneasHomePic.png')

    message = ''
    if request.method == "POST":
        name = request.form.get("symbol")
        name = name.upper()

        if controller.symbol_in_db(name):
            return redirect(url_for("stocks", stock=name)) 
        else:
            message = 'No matching results for '+ name

    return render_template("index.html", user_image1 = FinPic, user_image2 = homepic, errormessage=message)

@app.route("/news")
def news():
    message = ''
    FinPic = os.path.join(app.config['UPLOAD_FOLDER'], 'FINNEAS.png')
    data = controller.news_page()

    return render_template("news.html", user_image1 = FinPic, data=data, errormessage=message)

@app.route("/top_companies")
def company():
    message = ''
    FinPic = os.path.join(app.config['UPLOAD_FOLDER'], 'FINNEAS.png')
    
    data = controller.top_stocks_page()

    return render_template("top.html", user_image1 = FinPic, data=data, errormessage=message)

@app.route("/stocks/<stock>/overview", methods=['GET', 'POST'])
def stocks(stock):
    message = ''
    FinPic = os.path.join(app.config['UPLOAD_FOLDER'], 'FINNEAS.png')
    if request.method == "POST":
        d = request.form.get("timespan")
    else:
        d = 'day'

    data, labels, values, company_name = controller.stock_overview_page(stock, d)
    
    return render_template("stock.html", user_image1 = FinPic, data=data, stock=stock, labels=labels, values=values, company_name=company_name,errormessage=message)

@app.route("/stocks/<stock>/historical")
def historical(stock):
    message = ''
    FinPic = os.path.join(app.config['UPLOAD_FOLDER'], 'FINNEAS.png')

    data = controller.stock_historic_page(stock)
    return render_template("historical.html", user_image1 = FinPic, data=data, stock=stock, errormessage=message)

@app.route("/stocks/<stock>/analysis", methods=['GET', 'POST'])
def analysis(stock):
    message = ''
    FinPic = os.path.join(app.config['UPLOAD_FOLDER'], 'FINNEAS.png')

    if request.method == "POST":
        d = request.form.get("timespan")
    else:
        d = 'day'

    first_date, length, data = controller.stock_analysis_page(stock, d)

    return render_template("analysis.html", user_image1 = FinPic, stock=stock, first_date= first_date, length=length, chart_data=data, errormessage=message, timespan=d)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
 
 
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')


if __name__ == "__main__":
    app.run()
    #app.run(debug=True)
