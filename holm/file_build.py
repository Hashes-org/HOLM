import logging


class FileBuild:
  # TODO: if we keep this instance active, we could keep the keys loaded (using ram), and save space on rebuild
  input = None
  output = None
  type = None
  list = None
  keys = []
  add_data = {}
  rem_data = {}

  def __init__(self, inpath, keys, outpath, type, list=None):
    self.input = inpath
    self.output = outpath
    self.keys = keys
    self.type = type
    self.list = list

  def generate(self):
    logging.log(logging.DEBUG, "Load " + str(len(self.keys)) + " key files")
    add_count = 0
    rem_count = 0
    for key in self.keys:
      with open("data/keys/" + key + ".txt") as f:
        for line in f:
          line = line.strip("\r\n")
          action = line[0]
          if action == '-':
            self.rem_data[line[1:]] = True
            rem_count += 1
          elif action == '+':
            # decide if this add is affecting our build
            split = line[1:].split('|')
            left = split[0]
            list = split[1]
            hash = '|'.join(split[2:])
            if self.type == 'list':  # specific list - this might not be needed at all
              pass
            else:  # global left list
              if left == self.type:  # only add it if it's for the right type
                self.add_data[hash] = True
                add_count += 1

    logging.log(logging.INFO, "Loaded " + str(add_count) + " potential entries to add and " + str(rem_count) + " potential entries to remove.")
    with open(self.input, "r", encoding='utf-8', errors='ignore') as infile:
      with open(self.output, "w") as outfile:
        for line in infile:
          line = line.strip("\r\n")
          if line in self.add_data.keys():
            self.add_data.pop(line)  # it's already added, so we don't need to add it
          if line.split(':')[0] not in self.rem_data.keys():
            outfile.write(line + "\n")

        # write add data to file which was not popped out yet
        for key in self.add_data.keys():
          outfile.write(key + "\n")
        outfile.close()
      infile.close()
    logging.log(logging.INFO, "Generation completed!")
