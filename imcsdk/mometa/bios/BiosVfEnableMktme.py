"""This module contains the general information for BiosVfEnableMktme ManagedObject."""

from ...imcmo import ManagedObject
from ...imccoremeta import MoPropertyMeta, MoMeta
from ...imcmeta import VersionMeta


class BiosVfEnableMktmeConsts:
    VP_ENABLE_MKTME_DISABLED = "Disabled"
    VP_ENABLE_MKTME_ENABLED = "Enabled"
    _VP_ENABLE_MKTME_DISABLED = "disabled"
    _VP_ENABLE_MKTME_ENABLED = "enabled"
    VP_ENABLE_MKTME_PLATFORM_DEFAULT = "platform-default"


class BiosVfEnableMktme(ManagedObject):
    """This is BiosVfEnableMktme class."""

    consts = BiosVfEnableMktmeConsts()
    naming_props = set([])

    mo_meta = {
        "classic": MoMeta("BiosVfEnableMktme", "biosVfEnableMktme", "Enable-Mktme", VersionMeta.Version421a, "InputOutput", 0x1f, [], ["admin"], ['biosPlatformDefaults', 'biosSettings'], [], [None]),
    }


    prop_meta = {

        "classic": {
            "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version421a, MoPropertyMeta.INTERNAL, None, None, None, None, [], []),
            "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version421a, MoPropertyMeta.READ_WRITE, 0x2, 0, 255, None, [], []),
            "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version421a, MoPropertyMeta.READ_WRITE, 0x4, 0, 255, None, [], []),
            "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version421a, MoPropertyMeta.READ_WRITE, 0x8, None, None, None, ["", "created", "deleted", "modified", "removed"], []),
            "vp_enable_mktme": MoPropertyMeta("vp_enable_mktme", "vpEnableMktme", "string", VersionMeta.Version421a, MoPropertyMeta.READ_WRITE, 0x10, None, None, None, ["Disabled", "Enabled", "disabled", "enabled", "platform-default"], []),
        },

    }

    prop_map = {

        "classic": {
            "childAction": "child_action", 
            "dn": "dn", 
            "rn": "rn", 
            "status": "status", 
            "vpEnableMktme": "vp_enable_mktme", 
        },

    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.status = None
        self.vp_enable_mktme = None

        ManagedObject.__init__(self, "BiosVfEnableMktme", parent_mo_or_dn, **kwargs)

