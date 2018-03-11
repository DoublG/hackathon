from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession, SQLContext,dataframe as df,group
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
import os
from shutil import rmtree
import argparse

appName = "Rating Application"
master = "local"
root_folder = os.path.abspath(os.path.dirname(__file__))


def predict_all(model, user_product, categories):
    predictions = model.predictAll(user_product.rdd).toDF()

    info = predictions.join(categories, predictions.product == categories.productID)\
        .select(predictions.user, predictions.product, predictions.rating, categories.ProductText.alias('text'))

    info.show(n=500)


def save_model(sc, model):
    path = os.path.join(root_folder, '../data/likeModel')

    try:
        rmtree(path)
    except:
        pass

    model.save(sc, path)


def calculate_initial_rating():
    sc = SparkContext(conf=SparkConf().setAppName(appName).setMaster(master))
    sql = SQLContext(sc)

    user_likes = \
        sql.read.csv(path=os.path.join(root_folder, '../data/recommendation/user_likes.csv'),
            schema='''userID INT, productID INT, rating DOUBLE''', header=True)\
            .groupby('userID', 'productID').avg("rating")

    categories = \
        sql.read.csv(path=os.path.join(root_folder, '../data/recommendation/categories.csv'), header=True)

    model = ALS.train(user_likes, 10, 10)

    user_product = user_likes.select(user_likes.userID.alias('user'), user_likes.productID.alias('product')).distinct()

    predict_all(model, user_product, categories)

    save_model(sc, model)

    sc.stop()

def update_rating():
    parser = argparse.ArgumentParser(description='Add new recommendation')
    parser.add_argument("userID", help="User id")
    parser.add_argument("productID", help="Product id")
    parser.add_argument("rating", help="Rating")
    args = parser.parse_args()

    sc = SparkContext(conf=SparkConf().setAppName(appName).setMaster(master))
    sql = SQLContext(sc)

    rating = sc.parallelize([Rating(args.userID, args.productID, args.rating)])
    model = ALS.train(rating, 10, 10)

    prediction = model.predict(args.userID, args.productID)
    print('{} recomendation'.format(prediction))

    save_model(sc, model)

    sc.stop()