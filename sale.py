# -*- coding: utf-8 -*-
"""
    sale.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.pyson import Eval, Bool

__all__ = ['Sale']
__metaclass__ = PoolMeta

STATES = {
    'readonly': Eval('state') == 'done',
    'required': Bool(Eval('is_dhl_de_shipping')),
}

DHL_DE_PRODUCTS = [
    (None, ''),
    ('BPI', 'Weltpaket'),
    ('EPI', 'DHL Europaket'),
    ('EPN', 'DHL Paket'),
    ('EUP', 'GHL Europlus'),
    ('EXI (td)', 'Express Ident'),
    ('EXP (td)', 'DHL Express Paket'),
    ('OFP (td)', 'DHL Officepack'),
    ('RPN', 'Regional Paket AT'),
]

DHL_DE_EXPORT_TYPES = [
    (None, ''),
    ('0', 'Other'),
    ('1', 'Gift'),
    ('2', 'Sample'),
    ('3', 'Documents'),
    ('4', 'Goods Return'),
]

DHL_DE_INCOTERMS = [
    (None, ''),
    ('DDU', 'DDU'),
    ('CIP', 'CIP'),
    ('DDP', 'DDP'),
]


class Sale:
    "Sale"
    __name__ = 'sale.sale'

    is_dhl_de_shipping = fields.Function(
        fields.Boolean('Is Shipping', readonly=True),
        'get_is_dhl_de_shipping'
    )

    dhl_de_product_code = fields.Selection(
        DHL_DE_PRODUCTS, 'DHL DE Product Code', states=STATES, depends=[
            'state', 'is_dhl_de_shipping'
        ]
    )
    dhl_de_export_type = fields.Selection(
        DHL_DE_EXPORT_TYPES, 'DHL DE Export Type'
    )
    dhl_de_export_type_description = fields.Char(
        'Export Type Description'
    )
    dhl_de_terms_of_trade = fields.Selection(
        DHL_DE_INCOTERMS, 'Terms of Trade (incoterms)',
    )

    def get_is_dhl_de_shipping(self, name):
        """
        Ascertains if the sale is done using DHL (DE)
        """
        return self.carrier and self.carrier.carrier_cost_method == 'dhl_de'

    @fields.depends('is_dhl_de_shipping', 'carrier')
    def on_change_carrier(self):
        """
        Show/Hide dhl de Tab in view on change of carrier
        """
        res = super(Sale, self).on_change_carrier()

        res['is_dhl_de_shipping'] = self.carrier and \
            self.carrier.carrier_cost_method == 'dhl_de'

        return res

    def _get_shipment_sale(self, Shipment, key):
        """
        Downstream implementation which adds dhl-specific fields to the unsaved
        Shipment record.
        """
        ShipmentOut = Pool().get('stock.shipment.out')

        shipment = super(Sale, self)._get_shipment_sale(Shipment, key)

        if Shipment == ShipmentOut and self.is_dhl_de_shipping:
            shipment.dhl_de_product_code = self.dhl_de_product_code
            shipment.dhl_de_export_type = self.dhl_de_export_type
            shipment.dhl_de_export_type_description = \
                self.dhl_de_export_type_description
            shipment.dhl_de_terms_of_trade = self.dhl_de_terms_of_trade

        return shipment
