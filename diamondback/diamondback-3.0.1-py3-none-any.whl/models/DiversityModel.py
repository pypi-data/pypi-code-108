""" **Description**
        A diversity model realizes the selection and retention of a state as a
        finite collection of observations extracted from an incident signal, to
        maximize a minimum distance between any members of a state, according to
        a specified style or distance metric.

        .. math::
            d_{k} = \min(\ d_{u,v}\ )\quad\quad u, v \\in [\ 0,\ M\ ),\ u \\neq v

        .. math::
            d_{k} \geq d_{n}\qquad \longrightarrow\qquad d_{n} = d_{k}

        A diversity model is an opportunistic unsupervised learning model which
        typically improves condition and numerical accuracy and reduces storage
        relative to alternative approaches including generalized linear inverse.

        A state array of a specified order is defined.  A stationary dimension is
        inferred.  A style and order are specified.

        Style is in ( 'Chebyshev', 'Euclidean', 'Geometric', 'Manhattan' ).

        * | 'Chebyshev' distance is an L-infinity norm, a maximum absolute difference
          | in any dimension.

        .. math::
            d_{u,v} = \max(\ |\ \\vec{x_{u}} - \\vec{x_{v}}\ |\ )

        * | 'Euclidean' distance is an L-2 norm, a square root of a sum of squared
          | differences in each dimension.

        .. math::
            d_{u,v} = \matrix{\sum_{i=0}^{N}(\ |\ \\vec{x_{u,i}} - \\vec{x_{v,i}}\ )^2|}^{0.5}

        * | 'Geometric' distance is a ordered root of a product of absolute differences
          | in each dimension.

        .. math::
            d_{u,v} = \prod_{i=0}^{N}{(\ |\ \\vec{x_{u,i}} - \\vec{x_{v,i}}\ |\ )}^{\\frac{1}{N}}

        * | 'Manhattan' distance is an L-1 norm, a sum of absolute differences in each
          | dimension.

        .. math::
            d_{u,v} = \sum_{i=0}^{N}{\ (\ |\ \\vec{x_{u}} - \\vec{x_{v}}\ |\ )\ }

    **Example**
      
        ::
        
            from diamondback import DiversityModel

            # Create an instance.

            obj = DiversityModel( style = 'Euclidean', order = 4 )

            # Model an incident signal and extract a state.

            x = numpy.random.rand( 2, 32 )
            y = obj.model( x )
            s = obj.s

    **License**
        `BSD-3C.  <https://github.com/larryturner/diamondback/blob/master/license>`_
        © 2018 - 2022 Larry Turner, Schneider Electric Industries SAS. All rights reserved.

    **Author**
        Larry Turner, Schneider Electric, Analytics & AI, 2018-02-08.
"""

from typing import List, Union
import numpy

class DiversityModel( object ) :

    """ Diversity model.
    """

    __distance = dict( Chebyshev = lambda x, y : max( abs( x - y ) ),
                       Euclidean = lambda x, y : sum( ( x - y ) ** 2 ) ** 0.5,
                       Geometric = lambda x, y : numpy.prod( abs( x - y ) ) ** ( 1.0 / len( x ) ),
                       Manhattan = lambda x, y : sum( abs( x - y ) ) )

    @property
    def s( self ) :

        """ s : Union[ List, numpy.ndarray ] - state.
        """

        return self._s

    @s.setter
    def s( self, s : Union[ List, numpy.ndarray ] ) :

        self._s = s

    def __init__( self, style : str, order : int ) -> None :

        """ Initialize.

            Arguments :
                style : str - in ( 'Chebyshev', 'Euclidean', 'Geometric', 'Manhattan' ).
                order : int.
        """

        if ( ( not style ) or ( style not in DiversityModel.__distance ) ) :
            raise ValueError( f'style = {style}' )
        if ( order <= 0 ) :
            raise ValueError( f'Order = {order}' )
        super( ).__init__( )
        self._distance = DiversityModel.__distance[ style ]
        self._diversity = 0.0
        self._s = numpy.zeros( ( 0, order + 1 ) )

    def clear( self ) -> None :

        """ Clears an instance.
        """

        self._diversity = 0.0
        self.s = numpy.zeros( ( 0, self.s.shape[ 1 ] ) )

    def model( self, x : Union[ List, numpy.ndarray ] ) -> numpy.ndarray :

        """ Models an incident signal and produces a reference signal.

            Arguments :
                x : Union[ List, numpy.ndarray ] - incident signal.

            Returns :
                y : numpy.ndarray - diversity.
        """

        if ( ( not numpy.isscalar( x ) ) and ( not isinstance( x, numpy.ndarray ) ) ) :
            x = numpy.array( list( x ) )
        if ( ( len( x.shape ) > 2 ) or ( not len( x ) ) ) :
            raise ValueError( f'X = {x}' )
        if ( len( x.shape ) < 2 ) :
            rows, cols = 1, x.shape[ 0 ]
        else :
            rows, cols = x.shape
        if ( not self.s.shape[ 0 ] ) :
            self.s = numpy.zeros( ( rows, self.s.shape[ 1 ] ) ) + numpy.finfo( float ).max
        if ( ( rows != self.s.shape[ 0 ] ) or ( cols <= 0 ) ) :
            raise ValueError( f'Rows = {rows} Colums = {cols}' )
        cc = 0
        for jj in range( 0, self.s.shape[ 1 ] ) :
            if ( numpy.isclose( self.s[ 0, jj ], numpy.finfo( float ).max ) ) :
                break
            cc += 1
        y = numpy.zeros( cols )
        for jj in range( 0, cols ) :
            if ( cc < self.s.shape[ 1 ] ) :
                self.s[ :, cc ] = x[ :, jj ]
                cc += 1
            else :
                v, ii = self._diversity, -1
                for kk in range( 0, cc ) :
                    u, s = float( 'inf' ), numpy.array( self.s )
                    s[ :, kk ] = x[ :, jj ]
                    for uu in range( 0, cc - 1 ) :
                        for vv in range( uu + 1, cc ) :
                            d = self._distance( s[ :, uu ], s[ :, vv ] )
                            if ( d < u ) :
                                u = d
                    if ( u > v ) :
                        v, ii = u, kk
                if ( v > self._diversity ) :
                    self._diversity, self.s[ :, ii ] = v, x[ :, jj ]
            y[ jj ] = self._diversity
        return y
