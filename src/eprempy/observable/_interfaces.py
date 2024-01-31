import collections.abc
import pathlib
import typing
import sys

import numpy
import numpy.typing
from scipy import integrate
from scipy.interpolate import interp1d

from .. import aliased
from .. import container
from .. import datafile
from .. import etc
from .. import measured
from .. import metric
from .. import numeric
from .. import parameter
from .. import physical
from .. import quantity
from .. import reference
from .. import symbolic
from .. import universal
from ..reference import ARRAYS
from ._objects import (
    Arguments,
    Context,
    Quantity,
)


class Implementations:
    """Functional forms of all observable EPREM quantities."""

    def __init__(
        self,
        dataset: datafile.Arrays,
        axes: datafile.Axes,
        grid: aliased.Mapping[str, datafile.Array],
        constants: universal.Constants,
        parameters: parameter.Interface,
        system: metric.System,
    ) -> None:
        self._dataset = dataset
        self._axes = axes
        self._grid = grid
        self._constants = constants
        self._parameters = parameters
        self._system = system
        self._definitions = None

    @property
    def definitions(self):
        """A mapping from quantity name to canonical method."""
        if self._definitions is None:
            self._definitions = {
                'time': self.time,
                'energy': self.energy,
                'v': self.v,
                'mu': self.mu,
                'mass': self.mass,
                'charge': self.charge,
                'r': self.r,
                'theta': self.theta,
                'phi': self.phi,
                'br': self.br,
                'btheta': self.btheta,
                'bphi': self.bphi,
                'ur': self.ur,
                'utheta': self.utheta,
                'uphi': self.uphi,
                'rho': self.rho,
                'f': self.f,
                'x': self.x,
                'y': self.y,
                'z': self.z,
                'bmag': self.bmag,
                'umag': self.umag,
                'ubmag': self.ubmag,
                'angle': self.angle,
                'upara': self.upara,
                'udotb': self.udotb,
                'uperp': self.uperp,
                'divu': self.divu,
                'rigidity': self.rigidity,
                'mfp': self.mfp,
                'ar': self.ar,
                'average energy': self.average_energy,
                'energy density': self.energy_density,
                'flux': self.flux,
                'fluence': self.fluence,
                'intflux': self.intflux,
            }
        return self._definitions

    ## -- auxiliary/axis-like quantities --
    # Each method directly subscripts the dataset array because interpolation
    # over any of these quantities is either meaningless or unnecessary.

    def time(self, time=None) -> physical.Array:
        """Compute the output times."""
        return self.dataset.time[_normalize_indices(time or slice(None))]

    def energy(self, energy=None) -> physical.Array:
        """Compute the particle energies."""
        return self.dataset.energy[_normalize_indices(energy or slice(None))]

    def v(self, energy=None) -> physical.Array:
        """Compute the particle speeds."""
        return self.dataset.v[_normalize_indices(energy or slice(None))]

    def mu(self, mu=None) -> physical.Array:
        """Compute the particle pitch-angle cosines."""
        return self.dataset.mu[_normalize_indices(mu or slice(None))]

    def mass(self, species=None) -> physical.Array:
        """Compute the mass of each species."""
        return self.dataset.mass[_normalize_indices(species or slice(None))]

    def charge(self, species=None) -> physical.Array:
        """Compute the charge of each species."""
        return self.dataset.charge[_normalize_indices(species or slice(None))]

    ## -- primary observable quantities --
    # Each method accepts only the indices corresponding to the dataset
    # dimensions because it does not need to call other methods. It also accepts
    # arbitrary assumptions in case the user wants to interpolate over any of
    # the dataset dimensions.

    def r(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the radial observer coordinates."""
        return self._observe(
            self.dataset.r,
            assumptions,
            time=time,
            shell=shell,
        )

    def theta(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the polar observer coordinates."""
        return self._observe(
            self.dataset.theta,
            assumptions,
            time=time,
            shell=shell,
        )

    def phi(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the azimuthal observer coordinates."""
        return self._observe(
            self.dataset.phi,
            assumptions,
            time=time,
            shell=shell,
        )

    def br(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the magnetic-field radial component."""
        return self._observe(
            self.dataset.br,
            assumptions,
            time=time,
            shell=shell,
        )

    def btheta(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the magnetic-field polar component."""
        return self._observe(
            self.dataset.btheta,
            assumptions,
            time=time,
            shell=shell,
        )

    def bphi(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the magnetic-field azimuthal component."""
        return self._observe(
            self.dataset.bphi,
            assumptions,
            time=time,
            shell=shell,
        )

    def ur(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the velocity-field radial component."""
        return self._observe(
            self.dataset.ur,
            assumptions,
            time=time,
            shell=shell,
        )

    def utheta(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the velocity-field polar component."""
        return self._observe(
            self.dataset.utheta,
            assumptions,
            time=time,
            shell=shell,
        )

    def uphi(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the velocity-field azimuthal component."""
        return self._observe(
            self.dataset.uphi,
            assumptions,
            time=time,
            shell=shell,
        )

    def rho(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the plasma density."""
        return self._observe(
            self.dataset.rho,
            assumptions,
            time=time,
            shell=shell,
        )

    def f(
        self,
        time=None,
        shell=None,
        species=None,
        energy=None,
        mu=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the full particle distribution."""
        return self._observe(
            self.dataset.f,
            assumptions,
            time=time,
            shell=shell,
            species=species,
            energy=energy,
            mu=mu,
        )

    ## -- derived observable quantities --
    # Each method accepts all the indices required by the intermediate
    # quantities on which it depends. It also accepts arbitrary assumptions,
    # which it passes along to intermediate quantities.

    def x(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the x coordinate."""
        r = self.r(time, shell, assumptions)
        theta = self.theta(time, shell, assumptions)
        phi = self.phi(time, shell, assumptions)
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return r * numpy.sin(theta) * numpy.cos(phi)

    def y(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the y-axis coordinate."""
        r = self.r(time, shell, assumptions)
        theta = self.theta(time, shell, assumptions)
        phi = self.phi(time, shell, assumptions)
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return r * numpy.sin(theta) * numpy.sin(phi)

    def z(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the z-axis coordinate."""
        r = self.r(time, shell, assumptions)
        theta = self.theta(time, shell, assumptions)
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return r * numpy.cos(theta)

    def bmag(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the magnetic-field magnitude."""
        br = self.br(time, shell, assumptions)
        btheta = self.btheta(time, shell, assumptions)
        bphi = self.bphi(time, shell, assumptions)
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return numpy.sqrt(br**2 + btheta**2 + bphi**2)

    def umag(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the velocity-field magnitude."""
        ur = self.ur(time, shell, assumptions)
        utheta = self.utheta(time, shell, assumptions)
        uphi = self.uphi(time, shell, assumptions)
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return numpy.sqrt(ur**2 + utheta**2 + uphi**2)

    def ubmag(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute `umag * bmag`."""
        bmag = self.bmag(time, shell, assumptions)
        umag = self.umag(time, shell, assumptions)
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return bmag * umag

    def angle(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the angle between U and B."""
        udotb = self.udotb(time, shell, assumptions)
        ubmag = self.ubmag(time, shell, assumptions)
        ratio = udotb / ubmag
        arg = numpy.array(ratio)
        arg[arg < -1.0] = -1.0
        arg[arg > +1.0] = +1.0
        # NOTE: Intermediate methods in `_compute_angle` have already restricted
        # the result via subscription or interpolation.
        return physical.array(
            numpy.arccos(arg),
            unit='rad',
            axes=self.dataset.ur.axes,
        )

    def uperp(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the perpendicular velocity component."""
        umag = self.umag(time, shell, assumptions)
        upara = self.upara(time, shell, assumptions)
        uperpsqr = umag**2 - upara**2
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return numpy.sqrt(uperpsqr)

    def upara(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the parallel velocity component."""
        udotb = self.udotb(time, shell, assumptions)
        bmag = self.bmag(time, shell, assumptions)
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return udotb / bmag

    def udotb(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute U·B."""
        br = self.br(time, shell, assumptions)
        ur = self.ur(time, shell, assumptions)
        btheta = self.btheta(time, shell, assumptions)
        utheta = self.utheta(time, shell, assumptions)
        bphi = self.bphi(time, shell, assumptions)
        uphi = self.uphi(time, shell, assumptions)
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return br*ur + btheta*utheta + bphi*uphi

    def divu(
        self,
        time=None,
        shell=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the velocity divergence.

        The method computes ∇·U from the continuity equation, which can be
        written in the co-moving frame as

        ```
             1  dn
            --- -- = - div(U)
             n  dt
        ```

        where n represents density and d/dt is the convective derivative.
        """
        # NOTE: We first compute the entire array, then extract the subarray.
        rho = self.dataset.rho
        divu = -1.0 * numpy.gradient(rho, self.dataset.time, axis=0) / rho
        return self._observe(
            divu,
            assumptions,
            time=time,
            shell=shell,
        )

    def rigidity(
        self,
        species=None,
        energy=None,
    ) -> physical.Array:
        """Compute the magnetic rigidity.

        This method computes the particle momentum based on the relativistic
        relation E² = (K + mc²)² = p²c² + (mc²)², where K is the particles'
        kinetic energy. Finally, it divides the momentum by the particle charge
        to get rigidity.
        """
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return self._compute_rigidity(
            self.mass(species=species),
            self.charge(species=species),
            self.energy(energy=energy),
        )

    def _compute_rigidity(
        self,
        mass: physical.Array,
        charge: physical.Array,
        energy: physical.Array,
    ) -> physical.Array:
        """Internal computational logic for `_rigidity`.
        
        Notes
        -----
        - This method exists to support both `_rigidity`, which must have a
          function signature that conforms to what
          `observable.Context.implement` expects, and `_mfp`, which needs to be
          able to specify the energy argument.
        - This method requires that both `mass` and `scalar` be instances of
          `physical.Array`, which should always be true when they come from
          `self.mass` and `self.charge`.
        """
        if not isinstance(mass, physical.Array):
            raise TypeError(f"Wrong type for mass: {type(mass)}")
        if not isinstance(charge, physical.Array):
            raise TypeError(f"Wrong type for charge: {type(charge)}")
        c = self.constants['c'].asscalar
        j = energy / mass
        t = j.transpose('species', 'energy') + c**2
        p = numpy.sqrt(t**2 - c**4) * (mass / c)
        return p / charge

    def mfp(
        self,
        time=None,
        shell=None,
        species=None,
        energy=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the mean free path."""
        e = self.energy(energy=energy)
        m = self.mass(species=species)
        q = self.charge(species=species)
        rg = self._compute_rigidity(m, q, e)
        if not isinstance(e, physical.Array):
            raise TypeError(f"Wrong type for energy: {type(e)}")
        e0 = physical.array(
            [float(self.constants['MeV'])],
            unit=e.unit,
            axes=e.axes
        )
        rg0 = self._compute_rigidity(m, q, e0)
        r0 = self.constants['au'].asscalar
        r = self.r(time, shell, assumptions)
        rterm = (r / r0) ** self.parameters['mfpRadialPower']
        rgterm = (rg / rg0) ** self.parameters['rigidityPower']
        lambda0 = self.parameters['lambda0'].withunit(str(self.system))
        # NOTE: Intermediate methods have already restricted the result via
        # subscription or interpolation.
        return lambda0 * rterm * rgterm

    def ar(
        self,
        time=None,
        shell=None,
        species=None,
        energy=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the acceleration rate."""
        # NOTE: This method does not attempt to subscript intermediate
        # quantities by time or energy in case downstream code needs to
        # interpolate over them. It subscripts by shell because it assumes that
        # upstream code has reset `shell` as necessary for radial interpolation,
        # and it subscripts by species because interpolation over species is
        # meaningless.
        ar = self._compute_ar(shell=shell, species=species)
        return self._observe(ar, assumptions, time=time, energy=energy)

    def _compute_ar(self, shell=None, species=None) -> physical.Array:
        """Helper for `_ar`."""
        s = (
            shell if isinstance(shell, numeric.index.Sequence)
            else self.axes['shell'].index()
        )
        s1 = s.shift(1, ceil=len(self.axes['shell'])-1)
        s2 = s.shift(-1, floor=0)
        ur1 = self.ur(shell=s1)
        utheta1 = self.utheta(shell=s1)
        uphi1 = self.uphi(shell=s1)
        ur2 = self.ur(shell=s2)
        utheta2 = self.utheta(shell=s2)
        uphi2 = self.uphi(shell=s2)
        ux1 = self.umag(shell=s1)
        u1dotu2 = ur1*ur2 + utheta1*utheta2 + uphi1*uphi2
        one = physical.scalar(1)
        delta_u = ux1 * abs(one - u1dotu2 / (ux1*ux1))
        kxx1_ux1 = self._kxx_ux(shell=s1, species=species)
        kxx2_ux2 = self._kxx_ux(shell=s2, species=species)
        # NOTE: We can't directly compute delta_x = kxx1_ux1 + kxx2_ux2 because
        # the kxx_ux arrays have different shell axes.
        data = numpy.array(kxx1_ux1) + numpy.array(kxx2_ux2)
        if kxx1_ux1.unit != kxx2_ux2.unit:
            raise ValueError(
                "Units mismatch while computing acceleration rate"
            ) from None
        unit = kxx1_ux1.unit
        if kxx1_ux1.dimensions != kxx2_ux2.dimensions:
            raise ValueError(
                "Dimensions mismatch while computing acceleration rate"
            ) from None
        keys = {d for d in kxx1_ux1.dimensions if d != 'shell'}
        if any(kxx1_ux1.axes[k] != kxx2_ux2.axes[k] for k in keys):
            raise ValueError(
                "Axes mismatch while computing acceleration rate"
            ) from None
        axes = {
            k: physical.points(s) if k == 'shell' else v
            for k, v in kxx1_ux1.axes.items()
        }
        delta_x = physical.array(data, unit=unit, axes=axes)
        return delta_u / delta_x

    def _kxx_ux(self, **axes):
        """Helper for acceleration rate."""
        t = axes.get('time')
        s = axes.get('shell')
        p = axes.get('species')
        e = axes.get('energy')
        v = self.v(energy=e)
        mfp = self.mfp(time=t, shell=s, species=p, energy=e)
        theta = self.angle(time=t, shell=s)
        kper_kpar = self.parameters['kper / kpar']
        kxx_kpar = numpy.cos(theta)**2 + kper_kpar*numpy.sin(theta)**2
        kxx = mfp * kxx_kpar * v / 3.0
        ux = self.umag(time=t, shell=s)
        return kxx / ux

    def average_energy(
        self,
        time=None,
        shell=None,
        species=None,
        energy=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the average energy.

        This function first approximates the integral of v²f(v) with respect to
        v, where v is the particle velocity and f(v) is the isotropic
        distribution, then computes the energy density, divides that result by
        the intermediate result computed here, and finally divides by 2 to
        represent the kinetic energy. In MKS, for example, the particle
        velocities have the unit m/s and the isotropic distribution has the unit
        s³/m⁶, giving the intermediate value a unit of 1/m³. Dividing the energy
        density by this intermediate quantity yields a quantity with the unit J.
        Similar dimensional analysis yields a result of erg in cgs.
        """
        v = self.dataset.v
        dv = numpy.gradient(v, axis=-1)
        # NOTE: This method does not attempt to subscript the isotropic
        # distribution by time or energy in case downstream code needs to
        # interpolate over them. It subscripts by shell because it assumes that
        # upstream code has reset `shell` as necessary for radial interpolation,
        # and it subscripts by species because interpolation over species is
        # meaningless.
        fiso = self._fiso(shell=shell, species=species)
        normalizer = numpy.sum(v**2 * fiso * dv, axis=-1)
        epsilon = self.energy_density(shell=shell, species=species)
        array = 0.5 * epsilon / normalizer
        unit = self.system['energy'].unit
        result = self._observe(array, assumptions, time=time, energy=energy)
        return result.withunit(unit)

    def energy_density(
        self,
        time=None,
        shell=None,
        species=None,
        energy=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the energy density.

        This function first approximates the integral of v⁴f(v) with respect to
        v, where v is the particle velocity and f(v) is the isotropic
        distribution, then multiplies that result by the species mass. In MKS,
        for example, the particle velocities have units of m/s and the isotropic
        distribution has units of s³/m⁶, giving the intermediate value units of
        (m/s)⁵s³/m⁶, or 1/m/s². Multiplying by the mass yields an expression
        with units of kg/m/s², or J/m³. Similar dimensional analysis yields a
        result of erg/cm³ in cgs.
        """
        v = self.dataset.v
        dv = numpy.gradient(v, axis=-1)
        # NOTE: This method does not attempt to subscript the isotropic
        # distribution by time or energy in case downstream code needs to
        # interpolate over them. It subscripts by shell because it assumes that
        # upstream code has reset `shell` as necessary for radial interpolation,
        # and it subscripts by species because interpolation over species is
        # meaningless.
        fiso = self._fiso(shell=shell, species=species)
        array = self.mass(species) * numpy.sum(v**4 * fiso * dv, axis=-1)
        unit = self.system['energy / volume'].unit
        result = self._observe(array, assumptions, time=time, energy=energy)
        return result.withunit(unit)

    def flux(
        self,
        time=None,
        shell=None,
        species=None,
        energy=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the flux."""
        if self.dataset.hasflux:
            return self._observe(
                self.dataset.flux,
                assumptions,
                time=time,
                shell=shell,
                species=species,
                energy=energy,
            )
        # NOTE: This method does not attempt to subscript the isotropic
        # distribution by time or energy in case downstream code needs to
        # interpolate over them. It subscripts by shell because it assumes that
        # upstream code has reset `shell` as necessary for radial interpolation,
        # and it subscripts by species because interpolation over species is
        # meaningless. XXX: Maybe this method should check the assumptions
        # before deciding whether or not to subscript time and energy.
        fiso = self._fiso(shell=shell, species=species)
        e = self.energy()
        m = self.mass(species=species)
        g = physical.scalar(1.0, 'sr')
        array = 2 * fiso * e / (g * m**2)
        unit = self.system['flux'].unit
        result = array.withunit(unit)
        return self._observe(result, assumptions, time=time, energy=energy)

    def _fiso(
        self,
        time=None,
        shell=None,
        species=None,
        energy=None,
    ) -> physical.Array:
        """Compute the isotropic distribution."""
        if self.dataset.hasflux:
            flux = self._observe(
                self.dataset.flux,
                time=time,
                shell=shell,
                species=species,
                energy=energy,
            )
            m = self.mass(species=species)
            e = self.energy(energy=energy)
            # HACK: Explicitly construct an array in order to force the unit to
            # be the same. Otherwise, it will contain a solid-angle term.
            data = numpy.array((0.5 * flux * m**2) / e)
            unit = self.system['particle distribution'].unit
            return physical.array(data, unit=unit, axes=flux.axes)
        # NOTE: This method needs the full pitch-angle axis in order to
        # correctly compute the mean.
        f = self.f(time=time, shell=shell, species=species, energy=energy)
        return numpy.mean(f, axis=-1)

    def fluence(
        self,
        time=None,
        shell=None,
        species=None,
        energy=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute the fluence."""
        # NOTE: This method does not pass time to `flux` so that it can compute
        # the cumulative sum over the time axis before subscripting. However, it
        # allows `flux` to subscript and interpolate over energy.
        flux = self.flux(shell=shell, species=species, energy=energy)
        t = self.axes['time']
        it = t.indices
        t0 = self.time(time=it)
        tm = self.time(time=it.shift(-1, floor=0))
        dt = physical.array(
            numpy.array(t0) - numpy.array(tm),
            unit=t0.unit,
            axes={'time': t},
        )
        array = numpy.cumsum(flux * dt, axis=0)
        return self._observe(array, assumptions, time=time)

    def intflux(
        self,
        time=None,
        shell=None,
        species=None,
        assumptions: typing.Optional[dict]=None,
    ) -> physical.Array:
        """Compute intergral flux."""
        # NOTE: This method does not attempt to subscript flux by time in case
        # downstream code needs to interpolate over it. It does not attempt to
        # subscript flux by energy because it needs to integrate over that axis.
        # It subscripts by shell because it assumes that upstream code has reset
        # `shell` as necessary for radial interpolation, and it subscripts by
        # species because interpolation over species is meaningless.
        flux = self.flux(shell=shell, species=species)
        e = self.energy()
        minimum_energy = assumptions.pop('minimum_energy') or slice(None)
        intflux = self._integrate_flux(flux, e, minimum_energy)
        return self._observe(intflux, assumptions, time=time)

    def _integrate_flux(
        self,
        flux: physical.Array,
        energy: physical.Array,
        minimum_energy: parameter.ArgumentType,
    ) -> physical.Array:
        """Helper for `_intflux`."""
        if isinstance(minimum_energy, slice):
            return self._integrate_flux_slice(flux, minimum_energy)
        bounds = container.wrap(minimum_energy)
        data = numpy.zeros((*flux.shape[:-1], len(bounds)))
        for i, bound in enumerate(bounds):
            m = max(float(bound.withunit(energy.unit)), sys.float_info.min)
            y, x = self._check_interp(flux, energy, m)
            data[..., i] = integrate.simpson(y, x)
        unit = flux.unit * energy.unit
        extra = physical.axes({'minimum energy': minimum_energy})
        axes = flux.axes.without('energy', strict=True) | extra
        return physical.array(data, unit=unit, axes=axes)

    def _integrate_flux_slice(self, flux, bins: slice):
        energy = self.axes['energy']
        ie = energy.indices[bins]
        e0 = self.energy(energy=ie)
        em = self.energy(energy=ie.shift(-1, floor=0))
        de = physical.array(
            numpy.array(e0) - numpy.array(em),
            unit=e0.unit,
            axes={'energy': energy},
        )
        return numpy.cumsum(flux * de, axis=-1)

    def _check_interp(
        self,
        y: numpy.typing.ArrayLike,
        x: numpy.typing.ArrayLike,
        p: float,
    ) -> typing.Tuple[numpy.ndarray, numpy.ndarray]:
        """Interpolate `y` at `x = m` if necessary.

        This function uses an algorithm that interpolates `y` at `x = m` via a
        power law. If `m` is already in `x`, the interpolation leaves `y`
        unchanged. It was designed to support computations of integral flux and
        therefore currently only interpolates to a lower bound.

        This function converts both `x` and `y` to a ``numpy.ndarray`` before
        applying the algorithm.
        """
        xarr = numpy.array(x)
        yarr = numpy.array(y)
        if p < xarr.min():
            return yarr, xarr
        if xarr.ndim != 1:
            raise ValueError(
                "Expected a 1-D coordinate array"
            ) from None
        n = xarr.size
        m = yarr.shape[-1]
        if n != m:
            raise ValueError(
                f"The length of the final dimension of the interpolant ({m})"
                f" must equal the length of the coordinate array ({n})"
            ) from None
        i0, x0 = container.nearest(xarr, p, bound='upper')
        try:
            lnxc = numpy.log(xarr[i0+1] / x0)
        except IndexError as err:
            raise ValueError(
                f"The point {p} is outside the coordinate array {xarr}"
            ) from err
        lnfc = numpy.log(yarr[..., i0+1] / yarr[..., i0])
        beta = lnfc / lnxc
        base = numpy.full_like(beta, p / x0)
        xarr[i0] = p
        yarr[..., i0] *= numpy.power(base, beta)
        return yarr[..., i0:], xarr[i0:]

    def _observe(
        self,
        x: physical.Array,
        assumptions: typing.Optional[typing.Dict[str, typing.Any]]=None,
        **indices: physical.AxisType,
    ) -> physical.Array:
        # NOTE: The motivation for distinguishing `assumptions` from `indices`
        # (as opposed to passing both as, e.g., `**user`) is that the need to
        # interpolate over a canonical coordinate manifests as a key-value pair
        # for that coordinate in both the indices and assumptions.
        """Apply final data processing to an observable quantity."""
        if not isinstance(x, physical.Array):
            raise TypeError(
                f"Cannot observe non-array object of type {type(x)}"
            ) from None
        if not assumptions:
            return self._subscript(x, indices)
        return self._interpolate(x, indices, assumptions)

    def _subscript(
        self,
        x: physical.Array,
        indices: typing.Dict[str, physical.AxisType],
    ) -> physical.Array:
        """Subscript the array based on user indices."""
        # Each value represents the user-provided indices, if available, or a
        # full slice. The use of `user.indices.get(d) or slice(None)` instead of
        # `user.indices.get(d, slice(None))` forces a slice even if
        # `user.indices[d] == None`.
        axes = tuple(indices.get(d) or slice(None) for d in x.dimensions)
        return x[_normalize_indices(*axes)]

    def _interpolate(
        self,
        x: physical.Array,
        indices: typing.Dict[str, physical.AxisType],
        assumptions: typing.Dict[str, typing.Any]=None,
    ) -> physical.Array:
        """Interpolate the given array based on indices and assumptions."""
        interpolants = self._compute_interpolants(x, assumptions or {})
        base = interpolate(x, interpolants)
        default = {
            # Each value represents the appropriate default index for the
            # corresponding dimension of `x`, based on the size of that
            # dimension.
            d: numeric.index.value(0) if len(a) == 1 else slice(None)
            for d, a in base.axes.items()
        }
        finished = [
            # Each entry represents an interpolated dimension of `x`.
            'shell'if d in reference.ARRAYS.aliases['radius'] else d
            for d in interpolants
        ]
        axes = tuple(
            # Each value represents the user-provided indices, if available, or
            # the default indices for the corresponding dimension of `x`. The
            # use of `user.indices.get(d) or i` instead of `user.indices.get(d,
            # i)` forces the default value even if `user.indices[d] == None`.
            i if d in finished else indices.get(d) or i
            for d, i in default.items()
        )
        return base[_normalize_indices(*axes)]

    def _compute_interpolants(
        self,
        x: physical.Array,
        assumptions: dict,
    ) -> dict:
        """Determine the coordinate axes over which to interpolate."""
        from_axis = self._get_axis_interpolant(x, assumptions)
        if 'shell' not in x.dimensions:
            # The rest of this method deals with radial interpolation, which
            # only applies when 'shell' is one of the target quantity's
            # dimensions.
            return from_axis
        from_grid = self._get_grid_interpolant(x, assumptions, 'radius')
        return {**from_axis, **from_grid}

    def _get_axis_interpolant(self, x: physical.Array, assumptions: dict):
        """Compute interpolation information from an axis object."""
        interpolants = {}
        dimensions = {d for d in x.dimensions if d in self.grid}
        for key in dimensions:
            axis = self.axes.get(key)
            idx = x.axes[key].indices
            value = assumptions.get(key)
            if value is not None and isinstance(axis, physical.Coordinates):
                m = quantity.measure(value).withunit(axis.unit)
                a = physical.vector(axis[idx])
                for v in m:
                    _check_interpolation_bounds(key, v, a)
                interpolants[key] = Interpolant(
                    targets=numpy.array(m),
                    reference=self.grid[key][idx],
                )
        return interpolants

    def _get_grid_interpolant(
        self,
        x: physical.Array,
        assumptions: dict,
        name: str,
    ) -> dict:
        """Compute interpolation information from a grid object."""
        interpolants = {}
        idx = (x.axes['time'].indices, x.axes['shell'].indices)
        c = self.grid[name][idx]
        a = physical.tensor(c)
        try:
            key = next(
                alias for alias in reference.ARRAYS.aliases[name]
                if alias in assumptions
            )
        except StopIteration:
            return interpolants
        if value := assumptions.get(key):
            m = quantity.measure(value).withunit(str(self.system))
            for v in m:
                _check_interpolation_bounds(name, v, a)
            interpolants[key] = Interpolant(
                targets=numpy.array(m),
                reference=c,
            )
        return interpolants

    @property
    def dataset(self):
        """The available dataset arrays."""
        return self._dataset

    @property
    def constants(self):
        """The available physical constants."""
        return self._constants

    @property
    def parameters(self):
        """The available runtime parameter values."""
        return self._parameters

    @property
    def system(self):
        """The metric system."""
        return self._system

    @property
    def axes(self):
        """The available array-indexing objects."""
        return self._axes

    @property
    def grid(self):
        """The available coordinate-grid arrays."""
        return self._grid


def _normalize_indices(*args):
    """Normalize array-indexing objects."""
    if all(isinstance(v, numeric.index.Value) for v in args):
        return tuple(int(arg) for arg in args)
    return tuple(
        numeric.index.sequence([int(arg)])
        if isinstance(arg, numeric.index.Value) else arg
        for arg in args
    )


def _check_interpolation_bounds(
    dimension: str,
    value: measured.Object,
    reference: measured.Object,
) -> None:
    """Raise an exception if `value` is not bounded by `reference`."""
    a = numpy.min(reference)
    b = numpy.max(reference)
    if not a < value < b:
        sv = f"{float(value):6.4g} {str(value.unit)}"
        sa = f"{float(a):6.4g} {str(reference.unit)}"
        sb = f"{float(b):6.4g} {str(reference.unit)}"
        raise ValueError(
            f"Cannot interpolate {dimension!r} to {sv}"
            f". Value must be in [{sa}, {sb}]"
        ) from None


@etc.autostr
class Quantities(collections.abc.Mapping):
    """A collection of array-like observable quantities.

    Notes
    -----
    For each observable quantity, there is a public-facing property and an
    internal callback method, the latter of which becomes the `operator`
    property of the `~Context` instance from which this class will construct the
    corresponding `~Quantity` instance. The operator method calls a
    quantity-specific implementation that contains all the logic necessary for
    computing the appropriate array (possibly including calling other
    implementations), given user indices.
    """

    def __init__(
        self,
        source: pathlib.Path,
        config: pathlib.Path,
        system: metric.System,
    ) -> None:
        """Initialize this interface."""
        self._source = source
        self._config = config
        self._system = system
        self._dataset = None
        self._axes = None
        self._grid = None
        self._context = None
        self._parameters = None
        self._constants = None
        self._cache = {}
        self._coordinates = None
        self._defined = None
        self._functions = None

    def __len__(self):
        """Called for len(self)."""
        return len(self.defined)

    def __iter__(self):
        """Called for iter(self)."""
        return iter(self.defined)

    def __getitem__(self, __k: str) -> Quantity:
        """Retrieve an observable array by name."""
        if __k in self._cache:
            return self._cache[__k]
        built = self._build_observable(__k)
        self._cache[__k] = built
        return built

    def _build_observable(self, key: str, /):
        """Retrieve or create an observable quantity by name."""
        name = reference.OBSERVABLES.names.get(key, key)
        expression = symbolic.expression(name, raising='**')
        term = expression[0]
        result = self._get_observable(term.base)
        if len(expression) == 1:
            # We don't need to multiply or divide quantities.
            if term.exponent == 1:
                # We don't even need to raise this quantity to a power.
                return result
            return result ** term.exponent
        # We need to apply symbolic operations.
        this = result ** term.exponent
        if len(expression) > 1:
            for term in expression[1:]:
                result = self._get_observable(term.base)
                this *= result ** term.exponent
        return this

    def _get_observable(self, key: str):
        """Internal helper for building an observable quantity."""
        name = reference.OBSERVABLES.names.get(key, key)
        if name in self.defined:
            return getattr(self, name)
        raise KeyError(
            f"{key!r} is not an observable quantity"
        ) from None

    @property
    def time(self):
        """The output times."""
        return self._implement(
            self._time,
            self.dataset.time.unit,
            self.dataset.time.dimensions,
        )

    def _time(self, user: Arguments):
        """Callback method for time."""
        if 'time' in user:
            unit = self.dataset.time.unit
            data = numpy.array(user['time'].withunit(unit))
            return physical.array(
                data,
                unit=unit,
                axes=self.dataset.time.axes,
            )
        return self.functions.time(time=user.time)

    @property
    def energy(self):
        """The particle energies per nucleon."""
        return self._implement(
            self._energy,
            self.dataset.energy.unit,
            self.dataset.energy.dimensions,
        )

    def _energy(self, user: Arguments):
        """Callback method for particle energies per nucleon."""
        if 'energy' in user:
            unit = self.dataset.energy.unit
            data = numpy.array(user['energy'].withunit(unit))
            return physical.array(
                data,
                unit=unit,
                axes=self.dataset.energy.axes,
            )
        return self.functions.energy(energy=user.energy)

    @property
    def v(self):
        """The particle speed at each energy per nucleon."""
        return self._implement(
            self._v,
            self.dataset.v.unit,
            self.dataset.v.dimensions,
        )

    def _v(self, user: Arguments):
        """Callback method for equivalent particle speeds."""
        if 'energy' in user:
            energy = self._energy(user)
            mass = self.constants['mp'].asscalar
            return physical.array(numpy.sqrt(2 * energy / mass))
        return self.functions.v(energy=user.energy)

    @property
    def mu(self):
        """The particle pitch-angle cosines."""
        return self._implement(
            self._mu,
            self.dataset.mu.unit,
            self.dataset.mu.dimensions,
        )

    def _mu(self, user: Arguments):
        """Callback method for pitch-angle cosines."""
        if 'mu' in user:
            unit = self.dataset.mu.unit
            data = numpy.array(user['mu'].withunit(unit))
            return physical.array(
                data,
                unit=unit,
                axes=self.dataset.mu.axes,
            )
        return self.functions.mu(mu=user.mu)

    @property
    def mass(self):
        """The mass of each species."""
        return self._implement(
            self._mass,
            self.dataset.mass.unit,
            self.dataset.mass.dimensions,
        )

    def _mass(self, user: Arguments):
        """Callback method for species mass."""
        return self.functions.mass(species=user.species)

    @property
    def charge(self):
        """The charge of each species."""
        return self._implement(
            self._charge,
            self.dataset.charge.unit,
            self.dataset.charge.dimensions,
        )

    def _charge(self, user: Arguments):
        """Callback method for species charge."""
        return self.functions.charge(species=user.species)

    @property
    def r(self):
        """The radial observer coordinates."""
        return self._implement(
            self._r,
            self.dataset.r.unit,
            self.dataset.r.dimensions,
        )

    def _r(self, user: Arguments):
        """Callback method for radial coordinates."""
        return self.functions.r(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def theta(self):
        """The polar observer coordinates."""
        return self._implement(
            self._theta,
            self.dataset.theta.unit,
            self.dataset.theta.dimensions,
        )

    def _theta(self, user: Arguments):
        """Callback method for polar coordinates."""
        return self.functions.theta(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def phi(self):
        """The azimuthal observer coordinates."""
        return self._implement(
            self._phi,
            self.dataset.phi.unit,
            self.dataset.phi.dimensions,
        )

    def _phi(self, user: Arguments):
        """Callback method for azimuthal coordinates."""
        return self.functions.phi(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def br(self):
        """The magnetic-field radial component."""
        return self._implement(
            self._br,
            self.dataset.br.unit,
            self.dataset.br.dimensions,
        )

    def _br(self, user: Arguments):
        """Callback method for radial magnetic field."""
        return self.functions.br(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def btheta(self):
        """The magnetic-field polar component."""
        return self._implement(
            self._btheta,
            self.dataset.btheta.unit,
            self.dataset.btheta.dimensions,
        )

    def _btheta(self, user: Arguments):
        """Callback method for polar magnetic field."""
        return self.functions.btheta(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def bphi(self):
        """The magnetic-field azimuthal component."""
        return self._implement(
            self._bphi,
            self.dataset.bphi.unit,
            self.dataset.bphi.dimensions,
        )

    def _bphi(self, user: Arguments):
        """Callback method for azimuthal magnetic field."""
        return self.functions.bphi(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def ur(self):
        """The velocity-field radial component."""
        return self._implement(
            self._ur,
            self.dataset.ur.unit,
            self.dataset.ur.dimensions,
        )

    def _ur(self, user: Arguments):
        """Callback method for radial velocity."""
        return self.functions.ur(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def utheta(self):
        """The velocity-field polar component."""
        return self._implement(
            self._utheta,
            self.dataset.utheta.unit,
            self.dataset.utheta.dimensions,
        )

    def _utheta(self, user: Arguments):
        """Callback method for polar velocity."""
        return self.functions.utheta(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def uphi(self):
        """The velocity-field azimuthal component."""
        return self._implement(
            self._uphi,
            self.dataset.uphi.unit,
            self.dataset.uphi.dimensions,
        )

    def _uphi(self, user: Arguments):
        """Callback method for azimuthal velocity."""
        return self.functions.uphi(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def rho(self):
        """The plasma density."""
        return self._implement(
            self._rho,
            self.dataset.rho.unit,
            self.dataset.rho.dimensions,
        )

    def _rho(self, user: Arguments):
        """Callback method for plasma density."""
        return self.functions.rho(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def f(self):
        """The full particle distribution.
        
        Notes
        -----
        EPREM datasets generated with `streamFluxOutput=1` contain particle flux
        in place of this quantity. In those cases, the observable quantity will
        have the correct unit and dimensions, but calling its operator will
        unconditionally return `None`.
        """
        if self.dataset.hasdist:
            return self._implement(
                self._f,
                self.dataset.f.unit,
                self.dataset.f.dimensions,
            )
        unit = self.system['particle distribution'].unit
        dimensions = self.dataset.flux.dimensions | 'mu'
        return self._implement(self._f, unit, dimensions)

    def _f(self, user: Arguments):
        """Callback method for particle distribution."""
        if self.dataset.hasdist:
            return self.functions.f(
                time=user.time,
                shell=user.shell,
                species=user.species,
                energy=user.energy,
                mu=user.mu,
                assumptions=user.assumptions,
            )

    @property
    def x(self):
        """The x-axis observer coordinates given by x = r·sin(θ)cos(φ)."""
        return self._implement(
            self._x,
            self.r.unit,
            self.r.dimensions,
        )

    def _x(self, user: Arguments):
        """Callback method for x coordinates."""
        return self.functions.x(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def y(self):
        """The y-axis observer coordinates given by y = r·sin(θ)sin(φ)."""
        return self._implement(
            self._y,
            self.r.unit,
            self.r.dimensions,
        )

    def _y(self, user: Arguments):
        """Callback method for coordinates."""
        return self.functions.y(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def z(self):
        """The z-axis observer coordinates given by z = r·cos(θ)."""
        return self._implement(
            self._z,
            self.r.unit,
            self.r.dimensions,
        )

    def _z(self, user: Arguments):
        """Callback method for z coordinates."""
        return self.functions.z(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def bmag(self):
        """The magnetic-field magnitude, |B|."""
        return self._implement(
            self._bmag,
            self.br.unit,
            self.br.dimensions,
        )

    def _bmag(self, user: Arguments):
        """Callback method for magnetic-field magnitude."""
        return self.functions.bmag(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def umag(self):
        """The velocity-field magnitude, |U|."""
        return self._implement(
            self._umag,
            self.ur.unit,
            self.ur.dimensions,
        )

    def _umag(self, user: Arguments):
        """Callback method for velocity-field magnitude."""
        return self.functions.umag(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def angle(self):
        """The angle between the magnetic- and velocity-field vectors."""
        return self._implement(
            self._angle,
            self.system['plane angle'].unit,
            self.ur.dimensions,
        )

    def _angle(self, user: Arguments):
        """Callback method for flow angle."""
        return self.functions.angle(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def upara(self):
        """The velocity-field component parallel to the magnetic field."""
        return self._implement(
            self._upara,
            self.ur.unit,
            self.ur.dimensions,
        )

    def _upara(self, user: Arguments):
        """Callback method for parallel velocity."""
        return self.functions.upara(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def uperp(self):
        """The velocity-field magnitude perpendicular to the magnetic field."""
        return self._implement(
            self._uperp,
            self.ur.unit,
            self.ur.dimensions,
        )

    def _uperp(self, user: Arguments):
        """Callback method for perpendicular velocity."""
        return self.functions.uperp(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def divu(self):
        """The velocity-field divergence."""
        return self._implement(
            self._divu,
            1 / self.system['time'].unit,
            self.rho.dimensions,
        )

    def _divu(self, user: Arguments):
        """Callback method for flow divergence."""
        return self.functions.divu(
            time=user.time,
            shell=user.shell,
            assumptions=user.assumptions,
        )

    @property
    def rigidity(self):
        """The magnetic rigidity."""
        unit = self.system['momentum / charge'].unit
        dimensions = self.mass.dimensions | self.energy.dimensions
        return self._implement(
            self._rigidity,
            unit,
            dimensions,
        )

    def _rigidity(self, user: Arguments):
        """Callback method for rigidity."""
        return self.functions.rigidity(
            species=user.species,
            energy=user.energy,
        )

    @property
    def mfp(self):
        """The scattering mean free path."""
        unit = self.system['length'].unit
        dimensions = self.r.dimensions | self.rigidity.dimensions
        return self._implement(
            self._mfp,
            unit,
            dimensions,
        )

    def _mfp(self, user: Arguments):
        """Callback method for mean free path."""
        return self.functions.mfp(
            time=user.time,
            shell=user.shell,
            species=user.species,
            energy=user.energy,
            assumptions=user.assumptions,
        )

    @property
    def ar(self):
        """The theoretical acceleration rate."""
        unit = 1 / self.system['time'].unit
        return self._implement(
            self._ar,
            unit,
            self.mfp.dimensions,
        )

    def _ar(self, user: Arguments):
        """Callback method for acceleration rate."""
        return self.functions.ar(
            time=user.time,
            shell=user.shell,
            species=user.species,
            energy=user.energy,
            assumptions=user.assumptions,
        )

    @property
    def average_energy(self):
        """The average particle-distribution energy."""
        unit = self.energy.unit
        removed = self.energy.dimensions | self.mu.dimensions
        dimensions = self.f.dimensions - removed
        return self._implement(
            self._average_energy,
            unit,
            dimensions,
        )

    def _average_energy(self, user: Arguments):
        """Callback method for average energy."""
        return self.functions.average_energy(
            time=user.time,
            shell=user.shell,
            species=user.species,
            energy=user.energy,
            assumptions=user.assumptions,
        )

    @property
    def energy_density(self):
        """The particle-distribution energy density."""
        unit = self.system['energy density'].unit
        return self._implement(
            self._energy_density,
            unit,
            self.average_energy.dimensions,
        )

    def _energy_density(self, user: Arguments):
        """Callback method for energy density."""
        return self.functions.energy_density(
            time=user.time,
            shell=user.shell,
            species=user.species,
            energy=user.energy,
            assumptions=user.assumptions,
        )

    @property
    def flux(self):
        """The differential energy flux of a distribution."""
        unit = self.system['flux'].unit
        dimensions = self.f.dimensions - self.mu.dimensions
        return self._implement(
            self._flux,
            unit,
            dimensions,
        )

    def _flux(self, user: Arguments):
        """Callback method for particle flux."""
        return self.functions.flux(
            time=user.time,
            shell=user.shell,
            species=user.species,
            energy=user.energy,
            assumptions=user.assumptions,
        )

    @property
    def fluence(self):
        """The particle-distribution fluence."""
        unit = self.system['fluence'].unit
        return self._implement(
            self._fluence,
            unit,
            self.flux.dimensions,
        )

    def _fluence(self, user: Arguments):
        """Callback method for particle fluence."""
        return self.functions.fluence(
            time=user.time,
            shell=user.shell,
            species=user.species,
            energy=user.energy,
            assumptions=user.assumptions,
        )

    @property
    def intflux(self):
        """The integral flux of a distribution above a given energy"""
        unit = self.system['integral flux'].unit
        dimensions = self.flux.dimensions.replace('energy', 'minimum energy')
        return self._implement(
            self._intflux,
            unit,
            dimensions,
        )

    def _intflux(self, user: Arguments):
        """Callback method for integral particle flux."""
        assumptions = dict(user.assumptions)
        if 'minimum energy' not in assumptions:
            assumptions['minimum energy'] == sys.float_info.min
        return self.functions.intflux(
            time=user.time,
            shell=user.shell,
            species=user.species,
            assumptions=assumptions,
        )

    def _implement(
        self,
        operator: typing.Callable[[Arguments], physical.Array],
        /,
        unit: metric.Unit,
        dimensions: numeric.Dimensions,
    ) -> Quantity:
        """Implement an operation."""
        context = Context(operator, self.axes, self.grid)
        return Quantity(context, unit, dimensions)

    @property
    def defined(self):
        """The names and aliases of all observing implementations."""
        if self._defined is None:
            self._defined = [
                alias
                for k in self.functions.definitions
                for alias in reference.OBSERVABLES.aliases.get(k, [k])
            ]
        return self._defined

    @property
    def functions(self):
        """Functions corresponding to observable quantities."""
        if self._functions is None:
            self._functions = Implementations(
                self.dataset,
                self.axes,
                self.coordinates,
                self.constants,
                self.parameters,
                self.system,
            )
        return self._functions

    @property
    def grid(self):
        """The dataset coordinate-like arrays."""
        if self._grid is None:
            self._grid = datafile.grid(self.source, self.system)
        return self._grid

    @property
    def axes(self):
        """The array-indexing objects."""
        if self._axes is None:
            self._axes = datafile.axes(self.source, system=self.system)
        return self._axes

    @property
    def constants(self):
        """Fundamental physical constants in the given metric system."""
        if self._constants is None:
            self._constants = universal.Constants(str(self.system))
        return self._constants

    @property
    def coordinates(self):
        """The physical axes and pseudo-axes."""
        if self._coordinates is None:
            coordinates = {
                'time': self.dataset.time,
                'energy': self.dataset.energy,
                'mu': self.dataset.mu,
                'radius': self.dataset.r,
            }
            self._coordinates = aliased.Mapping(
                coordinates,
                aliases=reference.ALIASES,
            )
        return self._coordinates

    @property
    def dataset(self):
        """A view of the underlying dataset."""
        if self._dataset is None:
            self._dataset = datafile.arrays(self.source, self.system)
        return self._dataset

    @property
    def system(self):
        """The metric system of these quantities."""
        return self._system

    @property
    def source(self):
        """The data source."""
        return self._source

    @property
    def parameters(self):
        """The available runtime quantities."""
        if self._parameters is None:
            self._parameters = parameter.interface(self.config)
        return self._parameters

    @property
    def config(self):
        """The runtime configuration file."""
        return self._config


class Interpolant(typing.NamedTuple):
    """Attributes necessary for interpolation."""
    reference: physical.Array
    targets: numpy.ndarray


def interpolate(
    array: physical.Array,
    interpolants: typing.Mapping[str, Interpolant],
) -> physical.Array:
    """Interpolate a physical array.

    Parameters
    ----------
    array : `~Array`
        The array object to interpolate.

    interpolants : mapping from string to `~Interpolant`
    """
    if not interpolants:
        # If there are no interpolants, return the array as-is. This is simply a
        # convenience so that calling code need not check whether `interpolants`
        # is empty before calling this function.
        return array
    workspace = None
    axes = array.axes.copy()
    for dimension, interpolant in interpolants.items():
        workspace = _update_interpolation(
            array,
            interpolant.reference,
            interpolant.targets,
            workspace=workspace,
        )
        s = measured.sequence(interpolant.targets, interpolant.reference.unit)
        if dimension in ARRAYS.aliases['radius']:
            axes = axes.replace('shell', radius=physical.Coordinates(s))
        else:
            axes = axes.replace(dimension, physical.Coordinates(s))
    return array.spawn(workspace, unit=array.unit, axes=axes)


def _update_interpolation(
    array: physical.Array,
    reference: numeric.Array,
    targets: numpy.ndarray,
    workspace: numpy.ndarray=None,
) -> numpy.ndarray:
    """Helper for `~interpolate`."""
    x = numpy.array(array) if workspace is None else workspace
    indices = (array.dimensions.index(d) for d in reference.dimensions)
    dst, src = zip(*enumerate(indices))
    reordered = numpy.moveaxis(x, src, dst)
    interpolated = _apply_interpolation(reordered, reference, targets)
    return numpy.moveaxis(interpolated, dst, src)


def _apply_interpolation(
    data: numpy.typing.ArrayLike,
    reference: numpy.typing.ArrayLike,
    targets: typing.Iterable[float],
) -> numpy.ndarray:
    """Interpolate `data` to target values with respect to `reference`.

    This function will always interpolate over the leading dimension.

    Parameters
    ----------
    data : array-like
        The array-like object to interpolate. This function will convert `data`
        to a `numpy.ndarray`.

    reference : array-like
        The values at which `data` is known. This function will convert
        `reference` to a `numpy.ndarray`.

    targets : iterable of float
        The value(s) to which to interpolate `data`.

    Returns
    -------
    `numpy.ndarray`
        An array with the same shape as `array`, except for the interpolated
        dimension, which will have the same length as the number of values
        `targets`.
    """
    darray = numpy.array(data)
    rarray = numpy.array(reference)
    interpolated = [
        _apply_interp1d(darray, rarray, target)
        for target in targets
    ]
    if rarray.ndim == 2:
        return numpy.swapaxes(interpolated, 0, 1)
    return numpy.array(interpolated)


def _apply_interp1d(
    array: numpy.ndarray,
    reference: numpy.ndarray,
    target: float,
) -> typing.List[float]:
    """Interpolate data to `target` along the leading axis."""
    if target in reference:
        idx = container.nearest(reference, target).index
        return array[idx]
    ndim = reference.ndim
    if ndim == 2:
        interps = [interp1d(x, y, axis=0) for x, y in zip(reference, array)]
        return numpy.array([interp(target) for interp in interps])
    if ndim != 1:
        raise physical._array.NDimError(
            f"The reference array may have 1 or 2 (not {ndim}) dimensions"
        ) from None
    if reference.size == 1:
        # This works because we are interpolating over the leading dimension by
        # definition. Squeezing does not necessarily work because there may be
        # other singular dimensions.
        return array[0]
    interp = interp1d(reference, array, axis=0)
    return interp(target)


