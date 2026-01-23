# IPD-LLM-Agents2: Installation Instructions

## Status

✅ `config.py` - Written to platinum
✅ `ollama_agent.py` - Written to platinum
⏳ Remaining files need to be copied

## To Complete Installation

You have two options:

### Option 1: Extract from Archive (Easiest)

The complete system is in the downloaded `IPD-LLM-Agents2.tar.gz` file.

```bash
# On your local machine or wherever you downloaded the archive
cd /Users/dhart/mounts/platinum/work/forge/llm

# Extract (this will create IPD-LLM-Agents2 with all files)
tar -xzf ~/Downloads/IPD-LLM-Agents2.tar.gz

# Or if you need to overwrite the partial directory:
rm -rf IPD-LLM-Agents2
tar -xzf ~/Downloads/IPD-LLM-Agents2.tar.gz
```

### Option 2: Copy Individual Files

You need these additional files:
- `prompts.py` (5KB)
- `episodic_ipd_game.py` (15KB) 
- `test_episodic.py` (3.5KB)
- `run_batch.py` (8.5KB)
- `README.md`
- `IMPLEMENTATION_SUMMARY.md`
- `DEPLOYMENT.md`

All are available in the downloaded archive.

## After Installation

```bash
cd /Users/dhart/mounts/platinum/work/forge/llm/IPD-LLM-Agents2

# Test it
python test_episodic.py

# Run experiment
python episodic_ipd_game.py --episodes 5 --rounds 20
```

## Files Written So Far

- ✅ config.py (hyperparameters)
- ✅ ollama_agent.py (LLM agent wrapper)
- ⏳ prompts.py (needed)
- ⏳ episodic_ipd_game.py (needed - main code)
- ⏳ test_episodic.py (needed - for testing)
- ⏳ run_batch.py (needed - for experiments)

Extract the archive to get all files at once!
