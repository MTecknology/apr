'''
APR Model
'''
import apr.model.train


def entry_point():
    classifier = apr.model.train.AudioClassifier()
    classifier.training_loop()
