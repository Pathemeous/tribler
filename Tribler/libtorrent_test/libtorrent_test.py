import os
# from twisted.internet.defer import inlineCallbacks, Deferred
import libtorrent
from Tribler.Core.TorrentDef import TorrentDef
# from Tribler.Core.Utilities.twisted_thread import deferred
# from Tribler.Core.simpledefs import DLSTATUS_SEEDING, dlstatus_strings
from Tribler.Test.test_as_server import TESTS_DATA_DIR, TestAsServer
# from Tribler.dispersy.util import blocking_call_on_reactor_thread


class TestSeeding(TestAsServer):
    """
    Test whether the seeding works correctly.
    """

    def setUp(self, autoload_discovery=True):
        yield super(TestSeeding, self).setUp(autoload_discovery=autoload_discovery)
        self.test_deferred = Deferred()
        self.tdef = None
        self.sourcefn = None

    def setUpPreSession(self):
        super(TestSeeding, self).setUpPreSession()
        self.config.set_libtorrent(True)

    # def generate_torrent(self):
    #     self.tdef = TorrentDef()
    #     self.sourcefn = os.path.join(TESTS_DATA_DIR, 'video.avi')
    #     self.tdef.add_content(self.sourcefn)
    #     self.tdef.set_tracker("http://localhost/announce")
    #     self.tdef.finalize()
    #
    #     self.torrentfn = os.path.join(self.session.get_state_dir(), "gen.torrent")
    #     self.tdef.save(self.torrentfn)

    def start_download(self, dscfg):
        download = self.session.start_download_from_tdef(self.tdef, dscfg)
        download.set_state_callback(self.downloader_state_callback)

        download.add_peer(("127.0.0.1", self.seeder_session.get_listen_port()))

    def test_seeding(self):
        """
        Test whether a torrent is correctly seeded
        """
        session = libtorrent.session()
        session.listen_on(6881, 6891)
        testtorrent = lt.bdecode(open("fakeTorrent/testTorrent.torrent", 'rb').read())
        info = libtorrent.torrent_info(testtorrent)

        params = {'save_path': '.',
                  'storage_mode': libtorrent.storage_mode_t.storage_mode_sparse,
                  'ti': info}
        torrent_handle = session.add_torrent(params)

        def start_download(_):
            dscfg = self.dscfg_seed.copy()
            dscfg.set_dest_dir(self.getDestDir())
            self.start_download(dscfg)

        self.setup_seeder(self.tdef, TESTS_DATA_DIR).addCallback(start_download)
        return self.test_deferred

    def downloader_state_callback(self, ds):
        d = ds.get_download()
        self._logger.debug("download status: %s %s %s",
                           repr(d.get_def().get_name()),
                           dlstatus_strings[ds.get_status()],
                           ds.get_progress())

        if ds.get_status() == DLSTATUS_SEEDING:
            # File is in
            destfn = os.path.join(self.getDestDir(), "video.avi")
            f = open(destfn, "rb")
            realdata = f.read()
            f.close()
            f = open(self.sourcefn, "rb")
            expdata = f.read()
            f.close()

            self.assertEqual(realdata, expdata)
            self.test_deferred.callback(None)
            return 0.0, False
        return 1.0, False
