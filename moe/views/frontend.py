"""Frontend views for the MOE app."""
from pyramid.view import view_config

from moe.optimal_learning.EPI.src.python.constant import default_gaussian_process_parameters, default_ei_optimization_parameters


@view_config(route_name='home', renderer='moe:templates/index.mako')
def index_page(request):
    """The MOE index view."""
    return {
            'nav_active': 'home',
            }


@view_config(route_name='gp_plot', renderer='moe:templates/gp_plot.mako')
def gp_plot_page(request):
    """The MOE demo view."""
    return {
            'nav_active': 'demo',
            'default_gaussian_process_parameters': default_gaussian_process_parameters,
            'default_ei_optimization_parameters': default_ei_optimization_parameters,
            }