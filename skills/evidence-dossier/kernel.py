"""Entry points for the evidence-dossier skill.

Two calls, because the work spans two kernels: MCP connectors are reachable only
from the control-plane kernel, and api.crossref.org / api.datacite.org are not
reachable from there.

That split has a consequence for this file. A skill's kernel.py is auto-loaded
into the python/R kernels, NOT into the control-plane kernel — so the retrieval
entry point has to be reachable from a kernel where this file was never loaded
and where the skill directory may not be visible on disk. Hence `read`: pass a
function that returns a skill file's contents (host.skills.read), and the
modules are materialised into a working directory and imported from there.
Importing them from strings does not work — they resolve their own paths from
__file__, and identity.py has to sit beside them.
"""
import os
import sys

MODULE_NAMES = ("retrieve", "link", "extract", "present", "assemble")
SUPPORT_FILES = ("identity.py",)
MATERIALISE_DIR = ".evidence-dossier"


def dossier_skill_dir():
    """This skill's directory on disk, or None if the runtime hides it."""
    here = os.path.dirname(sys._getframe().f_code.co_filename)
    return here or None


def dossier_modules(read=None, workdir=None):
    """Load the pipeline modules.

    read=None: import them from the skill directory (works in python/R kernels).
    read=fn:   fn("retrieve.py") -> source; the files are written to `workdir`
               and imported from there (works anywhere, including the
               control-plane kernel).
    """
    import importlib.util
    if read is None:
        here = dossier_skill_dir()
        if not here:
            raise RuntimeError("skill directory unavailable here; pass read=lambda p: "
                               "host.skills.read('evidence-dossier', p)['content']")
    else:
        here = workdir or os.path.join(os.getcwd(), MATERIALISE_DIR)
        os.makedirs(here, exist_ok=True)
        for name in [n + ".py" for n in MODULE_NAMES] + list(SUPPORT_FILES):
            with open(os.path.join(here, name), "w") as fh:
                fh.write(read(name))
    out = {}
    for name in MODULE_NAMES:
        spec = importlib.util.spec_from_file_location(name, os.path.join(here, name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out[name] = mod
    return out


def dossier_retrieve(question, disconfirming, mcp, limits=None, outdir=None,
                     servers=None, read=None):
    """CONTROL-PLANE KERNEL (needs host.mcp). Search and write a run directory.

    Pass read=lambda p: host.skills.read("evidence-dossier", p)["content"] when
    calling from the control-plane kernel, where this file was not auto-loaded.

    `disconfirming` is REQUIRED and must be written as the negated claim, not
    derived from the question: a template that embeds the question retrieves the
    same literature (measured — it doubled the sources appearing in both query
    sets). Returns (run directory, retrieval stats).
    """
    if servers is None:
        servers = {"fasttrack": "fasttrack-literature", "consensus": "consensus",
                   "scispace": "scispace", "scholargw": "scholar-gateway"}
    M = dossier_modules(read=read)
    return M["retrieve"].run_live(question, mcp=mcp, servers=servers,
                                  disconfirming=disconfirming, limits=limits,
                                  outdir=outdir, check_integrity=False)


def dossier_build(rundir, llm, email=None, term_groups=None, max_concurrency=8, read=None):
    """ANALYSIS KERNEL (needs network + host.llm). Integrity, linkage, extraction, dossier.

    term_groups is optional; omitted, every source with usable text is shown.
    Supplied as a list of term lists, a source must match one term from every
    group and the groups are printed in the dossier. Returns (dossier path, stats).
    """
    M = dossier_modules(read=read)
    integ, tally = M["retrieve"].run_integrity(rundir, email=email)
    lstats = M["link"].run_link(rundir, net=True)[0]
    path, stats = M["assemble"].build(rundir, llm, term_groups=term_groups,
                                      max_concurrency=max_concurrency, mods=M)
    stats["integrity"] = tally
    stats["linkage"] = {"records": lstats.get("records"), "works": lstats.get("works")}
    return path, stats
