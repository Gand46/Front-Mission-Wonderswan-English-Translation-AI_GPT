# ChatGPT usage

For release QA, always create a patch and immediately run `verify`. BPS embeds
source, target and patch CRC32 values. The tool additionally reports SHA-256 of
source/target/output for reproducibility.

xdelta operations require `vendor/bin/xdelta3`, `WS_XDELTA3_BIN`, or a system
`xdelta3`. IPS/BPS do not require external binaries.
