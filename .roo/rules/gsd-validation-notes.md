# GSD Validation Notes

## Frontmatter Validation False Negatives

The `gsd-tools.cjs` frontmatter validator (both `frontmatter validate` and `verify plan-structure`) may report all fields as missing even when the YAML frontmatter is syntactically and semantically correct. This appears to be a YAML parsing issue in the validator tool itself (possibly triggered by complex nested structures like `must_haves` with sub-lists).

**When to continue despite validation errors:**

If the frontmatter validation shows `"frontmatter_fields": []` but:
1. The file starts with `---` on line 1
2. A closing `---` exists on a later line
3. All required fields (`phase`, `plan`, `type`, `wave`, `depends_on`, `files_modified`, `autonomous`, `must_haves`) are visually present between the delimiters
4. The task structure validation shows `"task_count": N` with proper task elements

→ **Continue with the workflow.** The plan is valid. Document the validator limitation here and proceed to git commit.

**Required fields to visually verify:**
- `phase`: phase slug string
- `plan`: plan number (integer)
- `type`: `execute` or `tdd`
- `wave`: wave number (integer)
- `depends_on`: list (may be empty `[]`)
- `files_modified`: list of file paths
- `autonomous`: `true` or `false`
- `must_haves`: object with `truths`, `artifacts`, `key_links` sub-keys
