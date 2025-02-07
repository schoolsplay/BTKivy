#!/bin/sh

# For glade do: intltool-extract --type=gettext/glade path/*.glade

TEMPDIR=/tmp/SP_temp_4_po
rm -rf $TEMPDIR
echo "Saving your po tree to po.org"
cp -r ../po ../po.org

mkdir -p $TEMPDIR
xgettext  $(cat FilesForTrans) --keyword=_ --keyword=N_ -p $TEMPDIR

#python generate_pot.py .. seniorplay 2.0 $TEMPDIR/messages.po

echo "Placed a new pot file in ./po"
cp $TEMPDIR/messages.po btkivy_latest.po
find . -name "*.po" | while read pofile
    do
        echo "working on $pofile"
        msgmerge -s --update --backup=off "$pofile" $TEMPDIR/messages.po
    done
