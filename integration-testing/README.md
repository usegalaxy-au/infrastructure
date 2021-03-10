## Integration testing

Have created a list of tools that can be used to test new server deployments. Based upon 3 different training network workflows. The idea is that the tools will be installed using ephemeris, tested with ephemeris and then the workflows run on the tutorial data. This will test a new server on a wide variety of tools and we can use these tests again when upgrading resources etc to check on times and effects etc.

### Workflows chosen 

Located in workflows directory as `.ga` files. Install with Ephemeris `workflow-install` command. You will need an admin api key.

1. Calling variants in non-diploid systems
2. qc-report (part of rna-seq reads to counts)
3. rna-seq reads to counts

### List of tools

Located in `all_tools.yml` in tools directory. Instal with Ephemeris `shed-tools install` command. You will need an admin api key.

- **rseqc**
  revisions:
  - f437057e46f1
</br>
- **picard**
  revisions:
  - a1f0b3f4b781
  - 2a17c789e0a5
</br>
- **samtools_idxstats**
  revisions:
  - 7a6034296ae9
  - 04d5581db1f5
</br>
- **multiqc**
  revisions:
  - 5e33b465d8d5
  - 1c2db0054039
</br>
- **collection_column_join**
  revisions:
  - 58228a4d58fe
</br>
- **fastqc**
  revisions:
  - c15237684a01
  - e7b2202befea
</br>
- **cutadapt**
  revisions:
  - 660cffd8d92a
</br>
- **hisat2**
  revisions:
  - 6daca6da3059
</br>
- **featurecounts**
  revisions:
  - 1759d845181e
</br>
- **bwa**
  revisions:
  - 3fe632431b68
</br>
- **bamtools_filter**
  revisions:
  - cb20f99fd45b
</br>
- **freebayes**
  revisions:
  - ef2c525bd8cd
</br>
- **vcffilter**
  revisions:
  - fa24bf0598f4
</br>
- **vcf2tsv**
  revisions:
  - 285060661b45


## Environment

Create a virtualenv (python3) with the dependencies from integration-testing/requirements.yml installed.

```
bash scripts/make_environment.sh
```

### TO DO

* Write better bash script arg parsing

