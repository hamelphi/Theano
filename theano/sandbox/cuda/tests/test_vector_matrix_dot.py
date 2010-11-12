import sys, time

from theano import shared
from theano.compile.pfunc import pfunc
from theano import tensor

import numpy
import theano
import theano.tensor as TT

# Skip test if cuda_ndarray is not available.
from nose.plugins.skip import SkipTest
import theano.sandbox.cuda as cuda_ndarray
if cuda_ndarray.cuda_available == False:
    raise SkipTest('Optional package cuda disabled')

import theano.sandbox.cuda as tcn
import theano.sandbox.cuda as cuda
import theano.sandbox.cuda.basic_ops as B
import theano.sandbox.cuda.blas as blasop
import theano.compile.mode
from theano.tests import unittest_tools as utt

### Tolerance factor used in this tests !!!
atol = 1e-6
##########################


if theano.config.mode=='FAST_COMPILE':
    mode_with_gpu = theano.compile.mode.get_mode('FAST_RUN').including('gpu')
    mode_without_gpu = theano.compile.mode.get_mode('FAST_RUN').excluding('gpu')
else:
    mode_with_gpu = theano.compile.mode.get_default_mode().including('gpu')
    mode_without_gpu = theano.compile.mode.get_default_mode().excluding('gpu')

def test_dot_vm():
    ''' Test vector dot matrix '''
    v = theano.shared( numpy.array(numpy.random.rand(2), dtype='float32'))
    m = theano.shared( numpy.array(numpy.random.rand(2,2),
                                   dtype='float32'))
    no_gpu_f = theano.function([], theano.dot(v,m), mode = mode_without_gpu)
    gpu_f    = theano.function([], theano.dot(v,m), mode = mode_with_gpu)
    # Assert they produce the same output
    assert numpy.allclose(no_gpu_f(), gpu_f(), atol = atol)
    # Assert that the gpu version actually uses gpu
    assert sum([isinstance(node.op, blasop.GpuDot22) for node in
                gpu_f.maker.env.toposort() ]) == 1

def test_dot_mv():
    ''' Test matrix dot vector '''
    v = theano.shared( numpy.array(numpy.random.rand(2), dtype='float32'))
    m = theano.shared( numpy.array(numpy.random.rand(2,2),
                                   dtype='float32'))
    no_gpu_f = theano.function([], theano.dot(m,v), mode = mode_without_gpu)
    gpu_f    = theano.function([], theano.dot(m,v), mode = mode_with_gpu)
    # Assert they produce the same output
    assert numpy.allclose(no_gpu_f(), gpu_f(), atol = atol)
    # Assert that the gpu version actually uses gpu
    assert sum([isinstance(node.op, blasop.GpuDot22) for node in
                gpu_f.maker.env.toposort() ]) == 1

def test_gemv1():
    ''' Is this the same test as test_gemv2 ? '''
    v1 = theano.shared( numpy.array(numpy.random.rand(2)  , dtype='float32'))
    v2 = theano.shared( numpy.array(numpy.random.rand(2)  , dtype='float32'))
    m  = theano.shared( numpy.array(numpy.random.rand(2,2), dtype='float32'))

    no_gpu_f = theano.function([], v2+theano.dot(m,v1), mode = mode_without_gpu)
    gpu_f    = theano.function([], v2+theano.dot(m,v1), mode = mode_with_gpu)
    # Assert they produce the same output
    assert numpy.allclose(no_gpu_f(), gpu_f(), atol = atol)
    # Assert that the gpu version actually uses gpu
    assert sum([isinstance(node.op, blasop.GpuGemm) for node in
                gpu_f.maker.env.toposort() ]) == 1


def test_gemv2():
    ''' Is this the same test as test_gemv1 ? '''
    v1 = theano.shared( numpy.array(numpy.random.rand(2)  , dtype='float32'))
    v2 = theano.shared( numpy.array(numpy.random.rand(2)  , dtype='float32'))
    m  = theano.shared( numpy.array(numpy.random.rand(2,2), dtype='float32'))

    no_gpu_f = theano.function([], v2+theano.dot(v1,m), mode = mode_without_gpu)
    gpu_f    = theano.function([], v2+theano.dot(v1,m), mode = mode_with_gpu)
    # Assert they produce the same output
    assert numpy.allclose(no_gpu_f(), gpu_f(), atol = atol)
    # Assert that the gpu version actually uses gpu
    assert sum([isinstance(node.op, blasop.GpuGemm) for node in
                gpu_f.maker.env.toposort() ]) == 1



if __name__=='__main__':
    test_dot_vm()
    test_dot_mv()
    test_gemv1()
    test_gemv2()
