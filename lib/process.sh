#!/bin/bash
# shellcheck disable=SC2016
SCRIPT="$0"



mnt="$temp" rootFS="${mnt}/root.x86_64";
packages=('dosfstools' 'ntfs-3g' 'parted' 'gdisk')
tarBall='archlinux-bootstrap-x86_64.tar.gz'
globalMirror="https://geo.mirror.pkgbuild.com"


packages2=('base' 'base-devel' 'linux' 'linux-firmware' 'linux-headers' 'efibootmgr' 'dosfstools' 'mtools' 'os-prober' 'grub' 'networkmanager' 'network-manager-applet' 'wget' 'pacutils' 'curl' 'git' 'cmake' 'extra-cmake-modules' 'intel-ucode' 'xf86-video-intel' 'vulkan-intel' 'mesa' 'intel-media-driver' 'alsa-utils' 'alsa-plugins' 'alsa-firmware' 'pulseaudio' 'xorg' 'xorg-server' 'xorg-xinit' 'zsh' 'nano' 'konsole' 'yay')

function try_catch() {
  local try_catch_error_code=0

  catch() {
    local try_catch_error_code=$?
    echo "An error occurred! Error code: $try_catch_error_code"
  }

  
  trap 'catch' ERR
  "$@"
  trap - ERR
  return $try_catch_error_code
}

function install_figma () {
  su -c "wget $FIGMA -O /tmp/figma-linux_0.10.0_linux_x64.pacman" "$USERNAME"
  pacman -U --needed --noconfirm '/tmp/figma-linux_0.10.0_linux_x64.pacman'
}

function install_miniconda () {
  su -c "wget $MINICONDA -O /tmp/miniconda.sh" "$USERNAME"
  su -c "chmod +x /tmp/miniconda.sh && ./tmp/miniconda.sh -b -p ~/.miniconda.sh" "$USERNAME" 
}

function install_ohmyzsh() {
  su -c "wget $OHMYZSH -O /tmp/ohmyzsh.sh" "$USERNAME"
  su -c "chmod +x /tmp/ohmyzsh.sh && ./tmp/ohmyzsh.sh" "$USERNAME"
}


function display_manager_catch () {

  display_manager_cdm () {
    cat <<EOF >> "/etc/.profile"
if [ "$(tty)" = '/dev/tty1' ]; then
    [ -n "$CDM_SPAWN" ] && return
    # Avoid executing cdm(1) when X11 has already been started.
    [ -z "$DISPLAY$SSH_TTY$(pgrep xinit)" ] && exec cdm
fi
EOF
  }
  display_manager_console_tdm () {
    echo "tdm --disable-xrunning-check" >> "/etc/.profile"
    sed -i "s:exec xterm -geometry 80x66+0+0 -name login:exec tdm --xstart:m" /etc/xinit/xinitrc
  }

  display_manager_ly () { 
    pacman -S --needed --noconfirm make automake gcc gcc-c++ kernel-devel pam-devel libxcb-devel
    systemctl enable ly.service
  };

  display_manager_emptty_git () { 
    su -c "touch ~/.emptty" "$USERNAME"
    cat <<EOF > "/home/$USERNAME/.emptty"
Selection=true
xrandr --output eDP1 --mode 1920x1080
xrdb -merge ~/.Xresources
# source /etc/profile does not have any effect
. /etc/profile
. ~/.bashrc
export BROWSER=firefox
export EDITOR=vim
exec dbus-launch \$@
EOF
   };
  display_manager_loginx () { 
    systemctl enable loginx@tty1
    systemctl disable getty@.service
   };
  display_manager_lermurs_git () { 
    systemctl enable lemurs.service
   };
  display_manager_entrance_git () { 
   echo "value $USERNAME string: 'entrance'" >> etc/entrance/entrance.conf;
   };
  display_manager_gdm () { 
    mkdir -p /apps/gdm/simple-greeter
    echo "true" > /apps/gdm/simple-greeter/banner_message_enable
    echo "ArchLinux" > /apps/gdm/simple-greeter/banner_message_text
    echo "true" > /apps/gdm/simple-greeter/disable_user_list
   };
  display_manager_sddm () { 
    systemctl enable sddm.service
   };
  display_manager_xorg_xdm () { 
    systemctl enable xdm.service
    echo "startxfce4" > "/home/$USERNAME/.xsession"
    chown "$USERNAME" "/home/$USERNAME/.xsession"; 
    chmod +x "/home/$USERNAME/.xsession"; chmod 755 "/home/$USERNAME/.xsession"
   };


  case $1 in
    display_manager_cdm) display_manager_cdm;;
    console-tdm) display_manager_console_tdm;;
    ly) display_manager_ly;;
    emptty-git) display_manager_emptty_git;;
    loginx) display_manager_loginx;;
    lemurs-git) display_manager_lermurs_git;;
    entrance-git) display_manager_entrance_git;;
    gdm) display_manager_gdm;;
    sddm) display_manager_sddm;;
    xorg-xdm) display_manager_xorg_xdm;;
  esac
}




function unpack () {
  wget "$globalMirror/iso/latest/$tarBall" -O "$temp"
  tar -xzf "${mnt}/${tarBall}" -C "$mnt" --numeric-owner;
  [[ -d '/usr/share/terminfo' ]] && cp -r '/usr/share/terminfo' "${rootFS}/usr/share/"
  printf 'Server = %s/$repo/os/$arch\n' "$globalMirror" >> "${rootFS}/etc/pacman.d/mirrorlist";

  cp -r "${SCRIPT}" "${rootFS}/install.sh"; cp -r "$temp/configfile" "${rootFS}/configfile";

  mount --bind "$rootFS" "$rootFS"; 
  "${rootFS}/bin/arch-chroot" "$rootFS" bash "install.sh" "-i";
}

function install () {
  source /configfile


  sleep 3
  systemd-machine-id-setup

  pacman-key --init; pacman-key --populate
  pacman -Syu --needed --noconfirm "${packages[@]}"

  pacman-key --recv-key 3056513887B78AEB --keyserver keyserver.ubuntu.com
  pacman-key --lsign-key 3056513887B78AEB
  pacman -Syu
  pacman -U --noconfirm 'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst' 'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst'
  
  {
    echo "[chaotic-aur]"
    echo "Include = /etc/pacman.d/chaotic-mirrorlist"
  } >> /etc/pacman.conf

  pacman -Syu

  partitions=("$EFI_PARTITION" "$SWAP_PARTITION" "$ROOT_PARTITION")
  for p in "${partitions[@]}"; do
    wipefs -a -f "$p" &>/dev/null
  done

  mkfs.fat -F 32 "$EFI_PARTITION"
  mkswap "$SWAP_PARTITION"
  mkfs.ext4 "$ROOT_PARTITION"

  mount "$ROOT_PARTITION" /mnt
  swapon "$SWAP_PARTITION"

  pacstrap -K /mnt "${packages2[@]}"
  genfstab -U /mnt >> /mnt/etc/fstab

  cp -r "$SCRIPT" /mnt/; cp -r configfile /mnt/configfile

  arch-chroot /mnt bash "$SCRIPT" "-s"
}

function setup () {

  function install_grub () {
    grub-install --bootloader-id='ArchLinux'
    grub-mkconfig -o /boot/grub/grub.cfg &>/dev/null
    mkdir -p /var/lock/dmraid &>/dev/null
    sed -i 's/#GRUB_DISABLE_OS_PROBER=false/GRUB_DISABLE_OS_PROBER=false/g' /etc/default/grub
    grub-mkconfig -o /boot/grub/grub.cfg
  }


  function create_user () {
    useradd -m "${1}"
    usermod -aG wheel "${1}"

    echo -e "${2}\n${2}" | passwd "$1"
    echo -e "${3}\n${3}" | passwd

    permissions=('%wheel ALL=(ALL:ALL) ALL' '%wheel ALL=(ALL:ALL) NOPASSWD: ALL' '%sudo ALL=(ALL:ALL) ALL')

    for permission in "${permissions[@]}"; do
      sed -i "s/# ${permission}/${permission}/g" /etc/sudoers
    done
  }


  function install_optionals () {
    su -c "yay -S --needed --noconfirm ${DESKTOP_ENVIRONMENT} ${DISPLAY_MANAGER} ${KERNEL}" "$USERNAME"
    su -c "yay -Syu --needed --noconfirm ${OPTIONALS[*]}" "$USERNAME"
  }


  source /configfile

  if [ ! -d /boot/efi ]; then
    mkdir -p /boot/efi
  fi

  mount "$EFI_PARTITION" /boot/efi

  install_grub

  create_user "${USERNAME}" "${UPASSWD}" "${RPASSWD}"

  ln -sf "/usr/share/zoneinfo/${TIMEZONE}" /etc/localtime
  echo "$HOSTNAME" > /etc/hostname; 
  echo "KEYBAORD=de-latin1-deadgraveacute" > /etc/vconsole.conf
  echo "LANG=$LANGUAGE" > /etc/locale.conf
  sed -i "s/#${LANGUAGE}/${LANGUAGE}/g" /etc/locale.gen && locale-gen

  pacman=('RootDir' 'DBPath' 'CacheDir' 'LogFile' 'GPGDir' 'HookkDir' 
  'XferCommand = /usr/bin/curl -L -C - -f -o %o %u'
  'UseSyslog' 'Color' 'ParallelDownloads = 5'
  )


  for pac in "${pacman[@]}"; do
    sed -i "s:#${pac}:${pac}:m" /etc/pacman.conf
  done

  try_catch install_optionals

  try_catch install_figma
  try_catch install_miniconda
  systemctl enable NetworkManager.service

  try_catch display_manager_catch

  try_catch install_ohmyzsh
}



case "$1" in
  -u)
    unpack;;
  -i)
    install;;
  -s)
    setup;;
esac





