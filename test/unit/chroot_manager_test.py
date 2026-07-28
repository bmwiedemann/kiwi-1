from unittest.mock import (
    patch, call, Mock
)
from pytest import raises

from kiwi.chroot_manager import (
    ChrootManager, ChrootMount
)

from kiwi.exceptions import (
    KiwiCommandError,
    KiwiUmountBusyError
)


class TestChrootManager:
    @patch('kiwi.chroot_manager.MountManager')
    @patch('kiwi.chroot_manager.Command.run')
    def test_run_in_chroot_context(self, mock_run, mock_mount):
        mock_mntMngr = Mock()
        mock_mount.return_value = mock_mntMngr
        with ChrootManager(
            '/some/root', binds=[
                ChrootMount('/dev'), ChrootMount('/proc'), ChrootMount('/sys')
            ]
        ) as chroot:
            chroot.run(['cmd', 'arg1', 'arg2'])
        assert mock_mount.call_args_list == [
            call(device='/dev', mountpoint='/some/root/dev'),
            call(device='/proc', mountpoint='/some/root/proc'),
            call(device='/sys', mountpoint='/some/root/sys')
        ]
        mock_run.assert_called_once_with(
            ['chroot', '/some/root', 'cmd', 'arg1', 'arg2'],
            None, True, False, True
        )
        mock_mntMngr.bind_mount.assert_called()
        mock_mntMngr.umount.assert_called()

    @patch('kiwi.chroot_manager.MountManager')
    @patch('kiwi.chroot_manager.Command.run')
    def test_run_fails_in_chroot_context(self, mock_run, mock_mount):
        mock_mntMngr = Mock()
        mock_mount.return_value = mock_mntMngr
        mock_run.side_effect = Exception
        with ChrootManager(
            '/some/root', binds=[
                ChrootMount('/dev'), ChrootMount('/proc'), ChrootMount('/sys')
            ]
        ) as chroot:
            with raises(Exception):
                chroot.run(['cmd', 'arg1', 'arg2'])
        assert mock_mount.call_args_list == [
            call(device='/dev', mountpoint='/some/root/dev'),
            call(device='/proc', mountpoint='/some/root/proc'),
            call(device='/sys', mountpoint='/some/root/sys')
        ]
        mock_run.assert_called_once_with(
            ['chroot', '/some/root', 'cmd', 'arg1', 'arg2'],
            None, True, False, True
        )
        mock_mntMngr.bind_mount.assert_called()
        mock_mntMngr.umount.assert_called()

    @patch('kiwi.chroot_manager.MountManager')
    @patch('kiwi.chroot_manager.Command.run')
    def test_run_fails_to_enter_chroot_context(self, mock_run, mock_mount):
        mock_mntMngr = Mock()
        mock_mount.return_value = mock_mntMngr
        mock_mntMngr.bind_mount.side_effect = KiwiCommandError('mount error')
        with raises(KiwiCommandError):
            with ChrootManager(
                '/some/root', binds=[
                    ChrootMount('/dev'), ChrootMount('/proc'),
                    ChrootMount('/sys')
                ]
            ) as chroot:
                chroot.run(['cmd', 'arg1', 'arg2'])
        assert mock_mount.call_args_list == [
            call(device='/dev', mountpoint='/some/root/dev'),
            call(device='/proc', mountpoint='/some/root/proc'),
            call(device='/sys', mountpoint='/some/root/sys')
        ]
        mock_run.assert_not_called()
        mock_mntMngr.bind_mount.assert_called_once()
        mock_mntMngr.umount.assert_called()

    @patch('kiwi.chroot_manager.MountManager')
    @patch('kiwi.chroot_manager.Command.run')
    def test_run_fails_to_enter_and_clean_chroot_context(
        self, mock_run, mock_mount
    ):
        mock_mntMngr = Mock()
        mock_mount.return_value = mock_mntMngr
        mock_mntMngr.bind_mount.side_effect = KiwiCommandError('mount error')
        mock_mntMngr.umount.side_effect = KiwiUmountBusyError('umount error')
        with raises(KiwiCommandError):
            with ChrootManager(
                '/some/root', binds=[
                    ChrootMount('/dev'), ChrootMount('/proc'),
                    ChrootMount('/sys')
                ]
            ) as chroot:
                chroot.run(['cmd', 'arg1', 'arg2'])
        assert mock_mount.call_args_list == [
            call(device='/dev', mountpoint='/some/root/dev'),
            call(device='/proc', mountpoint='/some/root/proc'),
            call(device='/sys', mountpoint='/some/root/sys')
        ]
        mock_run.assert_not_called()
        mock_mntMngr.bind_mount.assert_called_once()
        mock_mntMngr.umount.assert_called()

    @patch('kiwi.chroot_manager.MountManager')
    @patch('kiwi.chroot_manager.Command.run')
    def test_run_fails_to_clean_chroot_context(
        self, mock_run, mock_mount
    ):
        mock_mntMngr = Mock()
        mock_mount.return_value = mock_mntMngr
        mock_mntMngr.umount.side_effect = KiwiUmountBusyError('umount error')
        with raises(KiwiUmountBusyError):
            with ChrootManager(
                '/some/root', binds=[
                    ChrootMount('/dev'), ChrootMount('/proc'),
                    ChrootMount('/sys')
                ]
            ) as chroot:
                chroot.run(['cmd', 'arg1', 'arg2'])
        assert mock_mount.call_args_list == [
            call(device='/dev', mountpoint='/some/root/dev'),
            call(device='/proc', mountpoint='/some/root/proc'),
            call(device='/sys', mountpoint='/some/root/sys')
        ]
        mock_run.assert_called_once_with(
            ['chroot', '/some/root', 'cmd', 'arg1', 'arg2'],
            None, True, False, True
        )
        mock_mntMngr.bind_mount.assert_called()
        mock_mntMngr.umount.assert_called()

    @patch('kiwi.chroot_manager.MountManager')
    @patch('os.rmdir')
    @patch('os.path.exists')
    def test_created_mountpoints_are_removed(
        self, mock_exists, mock_rmdir, mock_mount
    ):
        # /some/root exists, the bind target below it does not
        mock_exists.side_effect = lambda path: path in [
            '/some/root', '/some', '/'
        ]
        with ChrootManager(
            '/some/root', binds=[ChrootMount('/var/tmp/kiwi_volumes.abc')]
        ):
            pass
        assert mock_rmdir.call_args_list == [
            call('/some/root/var/tmp/kiwi_volumes.abc'),
            call('/some/root/var/tmp'),
            call('/some/root/var')
        ]

    @patch('kiwi.chroot_manager.MountManager')
    @patch('os.rmdir')
    @patch('os.path.exists')
    def test_existing_mountpoints_are_kept(
        self, mock_exists, mock_rmdir, mock_mount
    ):
        mock_exists.return_value = True
        with ChrootManager('/some/root', binds=[ChrootMount('/dev')]):
            pass
        mock_rmdir.assert_not_called()

    @patch('kiwi.chroot_manager.MountManager')
    @patch('os.rmdir')
    @patch('os.path.exists')
    def test_non_empty_mountpoint_is_kept(
        self, mock_exists, mock_rmdir, mock_mount
    ):
        mock_exists.return_value = False
        mock_rmdir.side_effect = OSError('not empty')
        with ChrootManager('/some/root', binds=[ChrootMount('/dev')]):
            pass
        assert mock_rmdir.called
