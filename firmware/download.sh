#!/bin/bash
# SPDX-License-Identifier: 0BSD

# Copyright (C) 2022 by Forest Crossman <cyrozap@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
# PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.


curl -L -o bcm70012fw-20091229.bin https://github.com/yeradis/crystalhd/raw/7fa38a282db7af5a5746055f7c6cef8a9b8ee138/firmware/fwbin/70012/bcm70012fw.bin
curl -L -o bcm70012fw-20100712.bin https://github.com/yeradis/crystalhd/raw/bf3ab5fe081b1df220b35744d605ae38140c61ee/firmware/fwbin/70012/bcm70012fw.bin
curl -L -o bcm70012fw-20100714.bin https://github.com/yeradis/crystalhd/raw/222eaed6e68748240f89d5404d1a095a21c3077e/firmware/fwbin/70012/bcm70012fw.bin

curl -L -o bcm70015fw-20100326.bin https://github.com/yeradis/crystalhd/raw/5f9f9eb8eb85408b9c1e528ed7769824ffe5665b/firmware/fwbin/70015/bcm70015fw.bin
curl -L -o bcm70015fw-20100711.bin https://github.com/yeradis/crystalhd/raw/51d73bf0623cc1bbde257cfd4408a910ca24c5da/firmware/fwbin/70015/bcm70015fw.bin
curl -L -o bcm70015fw-20100714.bin https://github.com/yeradis/crystalhd/raw/222eaed6e68748240f89d5404d1a095a21c3077e/firmware/fwbin/70015/bcm70015fw.bin
curl -L -o bcm70015fw-20101123.bin https://github.com/yeradis/crystalhd/raw/433f44c018c495ae4e0734e5b6973293efd124bc/firmware/fwbin/70015/bcm70015fw.bin
curl -L -o bcm70015fw-20101130.bin https://github.com/yeradis/crystalhd/raw/cf2f76de247d3ead2bcb6af5823032e4a224f1f9/firmware/fwbin/70015/bcm70015fw.bin
