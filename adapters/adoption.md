# Full-checkout adoption (documented + locally tested)

Do not copy a standalone SKILL.md into global provider directories. This version
uses **one full, pinned toolkit checkout plus an explicit absolute tool root**.
This preserves sibling relationships, references, schemas and validator imports.
No provider-specific autoload format or symlink is required or promised.

1. Clone the desired toolkit revision, inspect it, and create its `.venv` as in README.
2. From the toolkit checkout run (replace TARGET with an existing project directory):

```sh
.venv/bin/python tools/adopt.py --target TARGET
```

3. Read `TARGET/.agent-workflow/ADOPTION.md`. Give your agent that file explicitly
   (using its normal file/context facility), then the named skill path from its table.
   It records absolute skill and interpreter/validator paths. No auto-discovery is claimed.
4. From **TARGET or any other directory**, run the literal absolute validation command
   in the adoption file with your bundle's absolute path. `--probe` additionally runs
   the shipped happy-path fixture with TARGET as cwd:

```sh
.venv/bin/python tools/adopt.py --target TARGET --probe
```

The installer refuses an existing adoption file unless `--check` is used to verify
an identical binding. It creates no symlinks, touches no global profile, modifies no
provider instructions and performs no git commit. Treat the target file as local:
it contains machine paths and should not be published. Relocating or upgrading the
checkout requires consciously removing the old adoption file and rerunning adoption.
The checkout must remain present and trusted. This is explicit context adoption,
not a native provider skill installer or a claim of cross-tool runtime support.
On Windows invoke `.venv/Scripts/python.exe`; Windows execution remains unverified.
