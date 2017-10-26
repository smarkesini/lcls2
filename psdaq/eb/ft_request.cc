#include "psdaq/eb/Endpoint.hh"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>

using namespace Pds::Fabrics;

static const char* PORT_DEF = "12345";
static const unsigned SIZE_DEF = 100;

static void showUsage(const char* p)
{
  printf("\nSimple libfabrics request example (its pair is the ft_push example).\n"
         "\n"
         "In this example the push server waits for a connection, and when a client connects the server\n"
         "it recieves a message containing info on a writable memory region on the client. The server then\n"
         "initiates a remote write to that memory and then waits for a disconnect from the client. After\n"
         "disconnect the server can accept new incoming connections.\n"
         "\n"
         "Usage: %s [-h|--help]\n"
         "    -a|--addr     the address of the server\n"
         "    -p|--port     the port or libfaric 'service' the server uses (default: %s)\n"
         "    -s|--size     the number of 64bit ints to read from the server (default: %u)\n"
         "    -h|--help     print this message and exit\n", p, PORT_DEF, SIZE_DEF);
}

int connect(Endpoint* endp, char* buff, size_t buff_size, int size)
{
  int num_comp;
  struct fi_cq_data_entry comp;

  // get a pointer to the fabric
  Fabric* fab = endp->fabric();
  // register the memory buffer
  MemoryRegion* mr = fab->register_memory(buff, buff_size);
  if (!mr) {
    fprintf(stderr, "Failed to register memory region: %s\n", fab->error());
    return fab->error_num();
  }

  RemoteAddress keys(mr->rkey(), (uint64_t) buff, buff_size);
  memcpy(buff, &keys, sizeof(keys));

  if(!endp->connect()) {
    fprintf(stderr, "Failed to connect endpoint: %s\n", endp->error());
    return endp->error_num();
  }

  // post a recv buffer for the completion data
  if (!endp->recv_comp_data()) {
    fprintf(stderr, "Failed posting completion recv from remote server: %s\n", endp->error());
    return endp->error_num();
  }

  // Send to the server where we want it to put the data
  if (!endp->send_sync(buff, sizeof (keys), mr)) {
    fprintf(stderr, "Failed receiving memory keys from remote server: %s\n", endp->error());
    return endp->error_num();
  }

  // wait for the completion generated by the remote write
  if (!endp->comp_wait(&comp, &num_comp, 1)) {
    fprintf(stderr, "Failed waiting for write completion data: %s\n", endp->error());
    return endp->error_num();
  }

  // check that this is the completion we want
  if ((comp.flags & FI_REMOTE_WRITE) && (comp.flags & FI_REMOTE_CQ_DATA)) {
    printf("write completion received! - server data value: %lu\n", comp.data);
    uint64_t* data_buff = (uint64_t*) buff;
    printf("data (key, addr, values): %lu %lu", keys.rkey, keys.addr);
    for(int j = 0; j < size; j++) {
      printf(" %lx", data_buff[j]);
    }
    printf("\n");
  } else {
    printf("WAT!\n");
  }

  return 0;
}

int main(int argc, char *argv[])
{
  int ret = FI_SUCCESS;
  bool show_usage = false;
  const char* addr = NULL;
  const char* port = PORT_DEF;
  unsigned size = SIZE_DEF;
  size_t buff_size = 0;
  char* buff = NULL;

  const char* str_opts = ":ha:p:s:";
  const struct option lo_opts[] =
  {
      {"help",  0, 0, 'h'},
      {"addr",  1, 0, 'a'},
      {"port",  1, 0, 'p'},
      {"size",  1, 0, 's'},
      {0,       0, 0,  0 }
  };

  int option_idx = 0;
  while (int opt = getopt_long(argc, argv, str_opts, lo_opts, &option_idx )) {
    if ( opt == -1 ) break;

    switch(opt) {
      case 'h':
        showUsage(argv[0]);
        return 0;
      case 'a':
        addr = optarg;
        break;
      case 'p':
        port = optarg;
        break;
      case 's':
        size = strtoul(optarg, NULL, 0);
        break;
      default:
        show_usage = true;
        break;
    }
  }

  if (optind < argc) {
    printf("%s: invalid argument -- %s\n", argv[0], argv[optind]);
    show_usage = true;
  }

  if (!addr) {
    printf("%s: server address is required\n", argv[0]);
    show_usage = true;
  }

  if (!size) {
    printf("%s: invalid size requested -- %u\n", argv[0], size);
    return 1;
  }

  if (show_usage) {
    showUsage(argv[0]);
    return 1;
  }

  buff_size = (size_t) size*sizeof(uint64_t);
  buff = new char[buff_size];

  Endpoint* endp = new Endpoint(addr, port);
  if (endp->state() != EP_UP) {
    fprintf(stderr, "Failed to initialize fabrics endpoint: %s\n", endp->error());
    ret = endp->error_num();
  } else {
    printf("using %s provider\n", endp->fabric()->provider());
    ret = connect(endp, buff, buff_size, size);
  }

  if (endp) delete endp;
  delete[] buff;

  return ret;
}
