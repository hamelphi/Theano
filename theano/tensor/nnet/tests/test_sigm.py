import unittest
import theano
from theano import tensor as T
from theano import gof
import numpy
from theano.tests import unittest_tools as utt
from theano.tensor.tests import test_basic as TT

from theano.tensor.nnet import *


class T_sigmoid(unittest.TestCase):
    def setUp(self):
        utt.seed_rng()
    def test_elemwise(self):
        utt.verify_grad(sigmoid, [numpy.random.rand(3,4)])

class T_softplus(unittest.TestCase):
    def setUp(self):
        utt.seed_rng()
    def test_elemwise(self):
        utt.verify_grad(softplus, [numpy.random.rand(3,4)])


class T_sigmoid_opts(unittest.TestCase):
    def test_exp_over_1_plus_exp(self):
        m = theano.config.mode
        if m == 'FAST_COMPILE':
            m = 'FAST_RUN'

        x = T.dvector()

        # tests exp_over_1_plus_exp
        f = theano.function([x], T.exp(x)/(1+T.exp(x)), mode=m)
        #theano.printing.debugprint(f)
        assert [node.op for node in f.maker.env.toposort()] == [sigmoid]

        # tests inv_1_plus_exp
        f = theano.function([x], T.fill(x,1.0) / (1+T.exp(-x)), mode=m)
        #theano.printing.debugprint(f)
        assert [node.op for node in f.maker.env.toposort()] == [sigmoid]

        # tests inv_1_plus_exp with neg
        f = theano.function([x], T.fill(x,-1.0) / (1+T.exp(-x)), mode=m)
        #theano.printing.debugprint(f)
        assert [node.op for node in f.maker.env.toposort()] == [sigmoid, 
                T.inplace.neg_inplace]

        # tests double inv_1_plus_exp with neg
        f = theano.function([x], (T.fill(x,-1.0)*T.exp(x)) / ((1+T.exp(x))*(1+T.exp(-x))), mode=m)
        #theano.printing.debugprint(f)
        assert [node.op for node in f.maker.env.toposort()] == [sigmoid, 
                T.mul]

    def test_1msigmoid(self):
        m = theano.config.mode
        if m == 'FAST_COMPILE':
            m = 'FAST_RUN'

        x = T.fmatrix()

        # tests exp_over_1_plus_exp
        f = theano.function([x], 1 - T.exp(x)/(1+T.exp(x)), mode=m)
        theano.printing.debugprint(f)
        assert [node.op for node in f.maker.env.toposort()] == [tensor.neg, sigmoid_inplace]

        # tests inv_1_plus_exp
        f = theano.function([x], 1 - T.fill(x,1.0) / (1+T.exp(-x)), mode=m)
        theano.printing.debugprint(f)
        assert [node.op for node in f.maker.env.toposort()] == [tensor.neg, 
                sigmoid_inplace]



