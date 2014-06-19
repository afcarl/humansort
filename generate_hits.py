import random

images = ['091_proto2.png', '079_proto2.png', '015_proto2.png',
          '059_proto2.png', '026_proto2.png', '075_proto2.png',
          '017_proto2.png', '004_proto2.png', '055_proto2.png',
          '003_proto2.png', '048_proto2.png', '085_proto2.png',
          '080_proto2.png', '094_proto2.png', '035_proto2.png',
          '032_proto2.png', '084_proto2.png', '081_proto2.png',
          '072_proto2.png', '041_proto2.png', '002_proto2.png',
          '006_proto2.png', '066_proto2.png', '082_proto2.png',
          '001_proto2.png', '095_proto2.png', '021_proto2.png',
          '054_proto2.png', '083_proto2.png', '057_proto2.png',
          '008_proto2.png', '064_proto2.png', '013_proto2.png',
          '014_proto2.png', '067_proto2.png', '097_proto2.png',
          '090_proto2.png', '065_proto2.png', '027_proto2.png',
          '058_proto2.png', '040_proto2.png', '047_proto2.png',
          '009_proto2.png', '076_proto2.png', '023_proto2.png',
          '046_proto2.png', '033_proto2.png', '018_proto2.png']

counts = {e:0 for e in images}

num_hits = 250
url_root = 'http://christopia.net/humansort/images/'
#url_root = 'http://protolab.cs.cmu.edu/humansort/images/'

pairs = []
links = {e:[] for e in images}

with open("hits.csv", "w") as f:
    f.write('image1url,image2url\n')

    for i in range(num_hits):
        sample = [img[2] for img in sorted([(counts[e], random.random(), e) for e
                                            in counts])][0:2]
        count = 0
        offset = 0
        while (sample[0], sample[1]) in pairs:
            sample = [img[2] for img in sorted([(counts[e], random.random(), e) for e
                                                in counts])][offset+0:offset+2]
            count += 1

            if count > 100:
                offset += 1
                count = 0


        counts[sample[0]] += 1
        counts[sample[1]] += 1
        pairs.append((sample[0], sample[1]))
        pairs.append((sample[1], sample[0]))
        links[sample[0]].append(sample[1])
        links[sample[1]].append(sample[0])

        f.write(url_root + sample[0] + ',' + url_root + sample[1] + '\n')

print(sum([counts[e] for e in counts]) / (1.0 * len(counts)))

checked = set()
queued = set()
queued.add(images[0])

while queued:
    image = queued.pop() 
    checked.add(image)
    for new_image in links[image]:
        if new_image not in checked.union(queued):
            queued.add(new_image)

for e in images:
    if e not in checked:
        print(e)
else:
    print("completely connected")

