# Imazen

Imazen builds image codecs, image processing and image servers. Our current work is an imaging stack in safe Rust: encoders and decoders for every major still-image format, the AV1 encoders behind AVIF, resizing, color management, compositing and perceptual quality metrics, and the pipeline and servers that put them to work.

[Website](https://www.imazen.io/) · [Pricing](https://www.imazen.io/pricing) · [Research dashboard](https://stats.lilith.now/) · [llms.txt](llms.txt)

## Products

| Product | What it is | Use it when |
|:--|:--|:--|
| [Imageflow Server](https://github.com/imazen/imageflow-server) | An image server for .NET: resize, crop, convert and optimize images on the fly from URL commands, with caching and request signing. Runs as a microservice, serverless, or inside an ASP.NET app.<br><sub>Latest release v0.9.0, 2025-07-04</sub> | You want images processed on request, close to your existing .NET stack. |
| [Imageflow](https://github.com/imazen/imageflow)<br><sub>[.NET](https://github.com/imazen/imageflow-dotnet) · [Node](https://github.com/imazen/imageflow-node) · [Go](https://github.com/imazen/imageflow-go)</sub> | The image processing engine (Rust, with a C API) behind Imageflow Server, plus imageflow_tool for the command line.<br><sub>Latest release v2.3.1-rc01, 2026-03-31</sub> | You process images ahead of time, in batch jobs, or from another language through the bindings. |
| [ImageResizer](https://github.com/imazen/resizer) | The long-running .NET image server and library that many ASP.NET sites still depend on.<br><sub>Latest release v5.1.0-rc01, 2025-06-26</sub> | You maintain an existing ImageResizer deployment. |

## Formats

One row per format, with the crates that read and write it. ↔ encode and decode, ← decode only.

| Format | | Crates | Status |
|:--|:-:|:--|:--|
| JPEG | ↔ | [zenjpeg](https://github.com/imazen/zenjpeg) | on crates.io |
| WebP | ↔ | [zenwebp](https://github.com/imazen/zenwebp) | on crates.io |
| AVIF | ↔ | [zenavif](https://github.com/imazen/zenavif) · [zenravif](https://github.com/imazen/cavif-rs) · [zenrav1e](https://github.com/imazen/zenrav1e) · [rav1d-safe](https://github.com/imazen/rav1d-safe) | on crates.io |
| PNG | ↔ | [zenpng](https://github.com/imazen/zenpng) | on crates.io |
| JPEG XL | ↔ | [jxl-encoder](https://github.com/imazen/jxl-encoder) · [zenjxl-decoder](https://github.com/imazen/zenjxl-decoder) | on crates.io |
| GIF | ↔ | [zengif](https://github.com/imazen/zengif) | on crates.io |
| HEIC | ← | [heic](https://github.com/imazen/heic) | on crates.io |
| AV1 video | ↔ | [zenav1-aom](https://github.com/imazen/zenav1-aom) · [zenav1-svt](https://github.com/imazen/zenav1-svt) · [zenrav1e](https://github.com/imazen/zenrav1e) · [rav1d-safe](https://github.com/imazen/rav1d-safe) | on crates.io |
| IMI | ↔ | [demo](https://gigapixels.imazen.org/) | format not frozen yet |
| JPEG AI | ↔ | [zenjpegai](https://github.com/imazen/zenjpegai) | unreleased |
| Cool-chic | ↔ | [zencoolchic](https://github.com/imazen/zencoolchic) | unreleased |
| TIFF | ↔ | [zentiff](https://github.com/imazen/zenextras) | unreleased; wraps our fork of an existing library |
| RAW · DNG | ← | [zenraw](https://github.com/imazen/zenraw) | on crates.io; built on existing libraries |
| BMP · PNM | ↔ | [zenbitmaps](https://github.com/imazen/zenbitmaps) | on crates.io |
| JPEG 2000 | ← | [zenjp2](https://github.com/imazen/zenextras) | unreleased; built on existing libraries |
| PDF | ← | [zenpdf](https://github.com/imazen/zenextras) | unreleased; built on existing libraries |
| SVG | ← | [zensvg](https://github.com/imazen/zenextras) | unreleased; built on existing libraries |

## Firsts

As far as we know, these were the first of their kind:

- JPEG XL encoder in Rust: [jxl-encoder](https://github.com/imazen/jxl-encoder)
- Full WebP codec in Rust (lossy and lossless, encode and decode): [zenwebp](https://github.com/imazen/zenwebp)
- JPEG AI codec in Rust: [zenjpegai](https://github.com/imazen/zenjpegai)
- SVT-AV1 encoder ported to Rust: [zenav1-svt](https://github.com/imazen/zenav1-svt)

## Choosing an integration

- **On request, from URLs.** [Imageflow Server](https://github.com/imazen/imageflow-server) resizes, crops and re-encodes images as they are requested, and caches the results.
- **Ahead of time.** `imageflow_tool` (in [Imageflow](https://github.com/imazen/imageflow)) and the [.NET](https://github.com/imazen/imageflow-dotnet), [Node](https://github.com/imazen/imageflow-node) and [Go](https://github.com/imazen/imageflow-go) bindings process images in build steps and batch jobs.
- **Inside a Rust program.** Depend on the codec crate for each format, or on the processing crates directly. Every topic in the project list below names the crate to start with.
- **With a coding agent.** Give it [https://raw.githubusercontent.com/imazen/imazen/main/llms.txt](https://raw.githubusercontent.com/imazen/imazen/main/llms.txt). It lists every entry with its version, license, docs and README, plus the rules above for picking one.

## Licensing

Codec and processing crates are mostly dual-licensed, `AGPL-3.0-only OR LicenseRef-Imazen-Commercial`: use them under the AGPL, or buy a commercial license at [imazen.io/pricing](https://www.imazen.io/pricing). Open-source projects, and companies with fewer than 5 employees and under $1M revenue, can get a key for $1. Shared APIs, pixel types, SIMD and utility crates are permissive, and some ports keep their upstream's license. Questions: sales@imazen.io.

Published crates by license, from crates.io on 2026-11-10:

| License | Crates |
|:--|:--|
| `MIT OR Apache-2.0` | archmage, cargo-copter, enough, garb, how-far, linear-srgb, magetypes, multiversed, webpx, whereat, winarm-cpufeatures, zenanalyze-api, zenbench, zenbitmaps, zencodec, zengif, zennode, zenpixels, zenpixels-convert, zenpredict, zensim, zenyuv |
| `AGPL-3.0-only OR LicenseRef-Imazen-Commercial` | heic, jxl-encoder, rav1d-safe, zenavif, zenblend, zenflate, zenjpeg, zenjxl, zenpng, zenquant, zenrav1e, zenravif, zenraw, zenresize, zentone, zenwebp |
| `BSD-3-Clause` | butteraugli, mozjpeg-rs, zenjxl-decoder |
| `Apache-2.0` | codec-corpus, zenzop |
| `MIT` | cargo-read |
| `BSD-2-Clause AND BSD-3-Clause AND MIT` | fast-ssim2 |
| `AGPL-3.0-or-later` | resamplescope-rs |

## How it is built

Codecs take bytes from strangers, usually on servers that hold other people's data, so a decoder bug is a security bug. Our crates compile with `#![forbid(unsafe_code)]`; SIMD goes through [archmage](https://imazen.github.io/archmage/), which wraps the intrinsics once. A few older crates still carry unsafe code, and we treat it as debt. Decoders and encoders take resource limits and cooperative cancellation ([enough](https://crates.io/crates/enough)), are fuzzed continually, and are tested bit for bit against C references where those exist; where pixels may differ, perceptual metrics ([zensim](https://github.com/imazen/zensim)) decide whether a person would see it. Details, with live figures: [the research dashboard](https://stats.lilith.now/).

## Who depends on it

- 45,592,280 downloads across crates.io and NuGet (4,693,763 on crates.io, 40,898,517 on NuGet).
- At least 2,569 GitHub repositories depend on [ImageResizer](https://github.com/imazen/resizer/network/dependents).
- 335 crates.io reverse dependencies across our crates.

<sub>As reported by each registry, captured 2026-10-27.</sub>

## Projects

Version numbers are the latest on crates.io; "unreleased" crates have source but no release yet.

| Topic | Projects |
|:--|:--|
| **JPEG**<br><sub>Encoders, decoder and YUV conversion, in safe Rust. Start with **zenjpeg**.</sub> | [zenjpeg](https://github.com/imazen/zenjpeg) <sub>0.8.4</sub> · [zenyuv](https://github.com/imazen/zenjpeg) <sub>0.1.3</sub> · [mozjpeg-rs](https://github.com/imazen/mozjpeg-rs) <sub>0.9.2</sub> · [browser-jpeg-support](https://github.com/lilith/browser-jpeg-support) |
| **WebP**<br><sub>Lossy and lossless WebP, plus libwebp bindings. Start with **zenwebp**.</sub> | [zenwebp](https://github.com/imazen/zenwebp) <sub>0.4.6</sub> · [webpx](https://github.com/imazen/webpx) <sub>0.4.1</sub> · [libwebp-net](https://github.com/imazen/libwebp-net) |
| **AVIF & AV1**<br><sub>The AVIF container, three AV1 encoders and a decoder. Start with **zenavif**.</sub> | [zenavif](https://github.com/imazen/zenavif) <sub>0.1.6</sub> · [zenavif-parse](https://github.com/imazen/zenavif) <sub>unreleased</sub> · [zenavif-serialize](https://github.com/imazen/zenavif) <sub>unreleased</sub> · [zenravif](https://github.com/imazen/cavif-rs) <sub>0.1.3</sub> · [zenrav1e](https://github.com/imazen/zenrav1e) <sub>0.1.4</sub> · [rav1d-safe](https://github.com/imazen/rav1d-safe) <sub>0.6.0</sub> · [zenav1-svt](https://github.com/imazen/zenav1-svt) <sub>unreleased</sub> · [zenav1-aom](https://github.com/imazen/zenav1-aom) <sub>unreleased</sub> |
| **JPEG XL**<br><sub>Encoder, decoder, GPU kernels and an inspector. Start with **jxl-encoder**.</sub> | [zenjxl](https://github.com/imazen/zenjxl) <sub>0.2.1</sub> · [zenjxl-decoder](https://github.com/imazen/zenjxl-decoder) <sub>0.3.10</sub> · [jxl-encoder](https://github.com/imazen/jxl-encoder) <sub>0.3.4</sub> · [jxl-gpu](https://github.com/imazen/jxl-gpu) · [jxl-inspect](https://github.com/imazen/jxl-inspect) <sub>unreleased</sub> |
| **PNG & GIF**<br><sub>PNG and animated GIF. Start with **zenpng**.</sub> | [zenpng](https://github.com/imazen/zenpng) <sub>0.1.4</sub> · [zengif](https://github.com/imazen/zengif) <sub>0.7.3</sub> |
| **HDR & gain maps**<br><sub>Ultra HDR gain maps and tone mapping. Start with **zentone**.</sub> | [ultrahdr](https://github.com/imazen/ultrahdr) · [zentone](https://github.com/imazen/zentone) <sub>0.1.0</sub> · [gainmap-spec-status](https://github.com/imazen/gainmap-spec-status) · [browser-hdr-test](https://github.com/lilith/browser-hdr-test) |
| **Learned codecs**<br><sub>JPEG AI and Cool-chic, ported to safe Rust. Unreleased. Start with **zenjpegai**.</sub> | [zenjpegai](https://github.com/imazen/zenjpegai) <sub>unreleased</sub> · [zencoolchic](https://github.com/imazen/zencoolchic) <sub>unreleased</sub> |
| **HEIC, RAW & more formats**<br><sub>HEIC, camera RAW, TIFF, PDF, SVG, JPEG 2000 and bitmaps. Start with **heic**.</sub> | [heic](https://github.com/imazen/heic) <sub>0.1.6</sub> · [zenraw](https://github.com/imazen/zenraw) <sub>0.2.0</sub> · [zenbitmaps](https://github.com/imazen/zenbitmaps) <sub>0.1.5</sub> · [zentiff](https://github.com/imazen/zenextras) <sub>unreleased</sub> · [zenpdf](https://github.com/imazen/zenextras) <sub>unreleased</sub> · [zensvg](https://github.com/imazen/zenextras) <sub>unreleased</sub> · [zenjp2](https://github.com/imazen/zenextras) <sub>unreleased</sub> |
| **Codec API & pipeline**<br><sub>The shared codec traits and the streaming pipeline that ties the codecs together. Start with **zencodec**.</sub> | [zencodec](https://github.com/imazen/zencodec) <sub>0.1.26</sub> · [zencodecs](https://github.com/imazen/zenpipe) <sub>unreleased</sub> · [zenpipe](https://github.com/imazen/zenpipe) <sub>unreleased</sub> · [zenlayout](https://github.com/imazen/zenpipe) <sub>unreleased</sub> · [zennode](https://github.com/imazen/zennode) <sub>0.1.1</sub> · [zenwasm](https://github.com/imazen/zenwasm) · [zentract](https://github.com/imazen/zentract) |
| **Processing**<br><sub>Resize, filter, blend, quantize, crop and enhance. Start with **zenresize**.</sub> | [zenresize](https://github.com/imazen/zenresize) <sub>0.3.1</sub> · [zenfilters](https://github.com/imazen/zenpipe) <sub>unreleased</sub> · [zenblend](https://github.com/imazen/zenblend) <sub>0.1.3</sub> · [zenquant](https://github.com/imazen/zenquant) <sub>0.1.3</sub> · [zensally](https://github.com/imazen/zensally) <sub>unreleased</sub> · [zensr](https://github.com/imazen/zensr) |
| **Pixels & color**<br><sub>Pixel formats, transfer functions and color conversion. Start with **zenpixels**.</sub> | [zenpixels](https://github.com/imazen/zenpixels) <sub>0.2.16</sub> · [zenpixels-convert](https://github.com/imazen/zenpixels) <sub>0.2.16</sub> · [linear-srgb](https://github.com/imazen/linear-srgb) <sub>0.6.12</sub> · [garb](https://github.com/imazen/garb) <sub>0.2.8</sub> |
| **Compression**<br><sub>DEFLATE, Zopfli, Zstandard and xxHash. Start with **zenflate**.</sub> | [zenflate](https://github.com/imazen/zenflate) <sub>0.4.1</sub> · [zenzop](https://github.com/imazen/zenzop) <sub>0.4.2</sub> · [zenzstd](https://github.com/imazen/zenzstd) <sub>unreleased</sub> · [zenhash](https://github.com/imazen/zenhash) <sub>unreleased</sub> |
| **Quality metrics**<br><sub>Perceptual quality metrics, used to tune the codecs. Start with **zensim**.</sub> | [zensim](https://github.com/imazen/zensim) <sub>0.2.7</sub> · [fast-ssim2](https://github.com/imazen/fast-ssim2) <sub>0.9.1</sub> · [butteraugli](https://github.com/imazen/butteraugli) <sub>0.9.3</sub> · [zenmetrics](https://github.com/imazen/zenmetrics) · [resamplescope-rs](https://github.com/imazen/resamplescope-rs) <sub>0.1.0</sub> · [squintly](https://github.com/imazen/squintly) <sub>unreleased</sub> · [evif](https://github.com/imazen/evif) <sub>unreleased</sub> |
| **Codec pickers**<br><sub>Choose the codec and quality for each image. Start with **zenpredict**.</sub> | [zenanalyze](https://github.com/imazen/zenanalyze) <sub>unreleased</sub> · [zenpredict](https://github.com/imazen/zenanalyze) <sub>0.2.0</sub> · [zenpicker](https://github.com/imazen/zenanalyze) <sub>unreleased</sub> · [zenanalyze-api](https://github.com/imazen/zenanalyze) <sub>0.1.0</sub> |
| **SIMD & Rust foundations**<br><sub>Safe SIMD, cooperative cancellation, error tracing and benchmarking. Start with **archmage**.</sub> | [archmage](https://github.com/imazen/archmage) <sub>0.9.31</sub> · [magetypes](https://github.com/imazen/archmage) <sub>0.9.31</sub> · [multiversed](https://github.com/imazen/multiversed) <sub>0.3.1</sub> · [winarm-cpufeatures](https://github.com/imazen/winarm-cpufeatures) <sub>0.1.2</sub> · [enough](https://github.com/imazen/enough) <sub>0.4.5</sub> · [how-far](https://github.com/imazen/how-far) <sub>0.1.0</sub> · [whereat](https://github.com/lilith/whereat) <sub>0.1.5</sub> · [zenbench](https://github.com/imazen/zenbench) <sub>0.1.11</sub> |

### Also

| Topic | Projects |
|:--|:--|
| **Test corpora**<br><sub>Images to test and train on.</sub> | [codec-corpus](https://github.com/imazen/codec-corpus) <sub>1.1.0</sub> · [imazen-26](https://github.com/imazen/imazen-26) · [imazen-26-jxl-p3](https://github.com/imazen/imazen-26-jxl-p3) · [imazen-26-jxl-srgb](https://github.com/imazen/imazen-26-jxl-srgb) · [imazen-26-originals](https://github.com/imazen/imazen-26-originals) · [imazen-xl-26](https://github.com/imazen/imazen-xl-26) · [all-the-images](https://github.com/imazen/all-the-images) · [zentrain-corpus](https://github.com/imazen/zentrain-corpus) |
| **Developer tools**<br><sub>Workspace, release and API tooling.</sub> | [cargo-copter](https://github.com/imazen/cargo-copter) <sub>0.3.0</sub> · [cargo-read](https://github.com/imazen/cargo-read) <sub>0.1.0</sub> · [crate-mcp](https://github.com/imazen/crate-mcp) <sub>unreleased</sub> · [cargo-superwork](https://github.com/imazen/cargo-superwork) <sub>unreleased</sub> · [zenutils](https://github.com/imazen/zenutils) · [efficient-ui](https://github.com/imazen/efficient-ui) |
| **Other tools**<br><sub>Everything else in use.</sub> | [astro-broken-link-checker](https://github.com/imazen/astro-broken-link-checker) · [folioxml](https://github.com/imazen/folioxml) · [interleaved-site](https://github.com/imazen/interleaved-site) |
| **Earlier work**<br><sub>The .NET and C years.</sub> | [keyhub](https://github.com/imazen/keyhub) · [hardwired](https://github.com/imazen/hardwired) · [imageflow-web](https://github.com/imazen/imageflow-web) · [repositext](https://github.com/imazen/repositext) · [imageflow-now](https://github.com/lilith/imageflow-now) · [suspension](https://github.com/imazen/suspension) · [imageci](https://github.com/imazen/imageci) · [srcset-checker](https://github.com/imazen/srcset-checker) · [bank-csv](https://github.com/imazen/bank-csv) · [load_image](https://github.com/lilith/load_image) <sub>unreleased</sub> |

## Demos

- [IMI](https://gigapixels.imazen.org/): Earth and deep-space imagery in IMI, Imazen's own image format for fast, independently addressable decoding. The format is not frozen yet.
- [JPEG AI in the browser](https://jpegai.imazen.org/): zenjpegai, the JPEG AI codec, running in the browser.
- [Metrics](https://metrics.imazen.org/): Compare images under the metrics in zenmetrics.
- [Metric cost](https://metric-brief.imazen.org/#models): What each of the ported image-quality metrics costs to run.
- [squintly](https://squintly.imazen.org/): Pairwise psychovisual data collection for zensim.
- [archmage docs](https://imazen.github.io/archmage/): Safe SIMD through capability tokens.

## Limitations

- Most crates are below 1.0 and their APIs still change between minor versions. Pin versions.
- Unreleased crates are listed so you can see where the work is going; do not build products on them yet.
- IMI, our own format, is not frozen; files written today may not decode with a later version.
- Figures here are snapshots: the inventory from 2026-10-28, registry facts from 2026-11-10.

## About this repository

`python3 tools/build.py --refresh` regenerates README.md and llms.txt from the public inventory behind the research dashboard (https://stats.lilith.now/data.json), crates.io and GitHub, plus the hand-written [catalog.toml](catalog.toml). Standard library only. Corrections are welcome as issues or pull requests against catalog.toml.

*Generated from inventory revision 5e25b0c42c4f (2026-10-28) and registry facts fetched 2026-11-10.*
