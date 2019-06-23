#! /usr/bin/perl -w
##! /share/local/bin/perl -w

use strict 'refs';
use lib '..';
use CGI qw(:standard);
use CGI::Carp qw/fatalsToBrowser/;


BEGIN {
  use CGI::Carp qw(carpout); # use nice error logging
  # redirect stderr to own log instead of server log
  
  $mapname="mun";  ## CHANGE for every script
  # ERRLOG should have +w permissions for world, and dir path x perms
  #$ERRLOG="$mapname.error_log";
  # path corrected to work on new server. /share/www can't be written to (tleipala, 2008-10-10)
  $ERRLOG="/share/logs/demos/ica/cocktail/$mapname.error_log";
  open(LOG, ">>$ERRLOG") or
    die("Unable to open my cgi error log $ERRLOG: $!\n");
  carpout(*LOG);
}     

$SOURCENAME = 'source';
$SOUNDFORMAT = 'wav';
$MIXEDNAME = 'mix';
$ESTNAME = 'est';
$IMAGEFORMAT = 'jpg';
$IMAGEPATH = 'gifs/';
$MAXSOURCES = 9;

sub headers
  {
    # print html-headers 
    print header();
    #print start_html(-title=>'Cocktail party demo'),"\n";
    print start_html(-title=>'Cocktail party demo',-style=>
    		     {'src'=>'cis_cocktail.css'}),"\n";
    print h1('COCKTAIL PARTY PROBLEM'),"\n";
    print p,'Imagine you\'re at a cocktail party. For you it is no problem to follow the discussion of your neighbours, even if there are lots of other sound sources in the room: other discussions in English and in other languages, different kinds of music, etc.. You might even hear a siren from the passing-by police car.',"\n";
    print p,'It is not known exactly how humans are able to separate the different sound sources.',"\n";
    print '<a href = "http://www.cs.helsinki.fi/u/ahyvarin/whatisica.shtml">Independent component analysis</a>',"\n";
    print 'is able to do it, if there are at least as many microphones or \'ears\' in the room as there are different simultaneous sound sources. In this demo, you can select which sounds are present in your cocktail party. ICA will separate them without knowing anything about the different sound sources or the positions of the microphones.',"\n";
 
  }
sub end_headers
  {

    print p,'<A HREF="http://www.cis.hut.fi/projects/ica/"><STRONG>ICA Research at Helsinki University of Technology</STRONG></A><BR>',"\n";
    print '<br clear=all><img src="/style/basic/gpixel.gif" height=1 width=1000 ALT=""><br>',"\n";
    print '<ADDRESS>',"\n";
    print '&copy <A HREF="mailto:jaakko.sarela@mail.cis.hut.fi"> Jaakko Särelä</A>, Patrik Hoyer and Ella Bingham, graphic design by Petri Saarikko.',"\n";
    print '<BR> 20-04-2005 </ADDRESS>',"\n";

    end_html;
  }

sub choose_sources
  {
    #my %boxlabels = (1=>'suomi 1',2=>'suomi 2',
    #		     3=>'englanti',4=>'musiikki 1',
    #                5=>'musiikki 2',6=>'kaupunki 1',7=>'kaupunki 2');

    print h2('SOUND SOURCES'),"\n";
    print p,'Select the <A href="sounds.html">sound sources</A> you wish by clicking the boxes under the icons.',"\n",'When you click the icons themselves you will hear a sample of the specific sound source.',"\n";
    print start_form,"\n";
    print '<TABLE BORDER="0" CELLPADDING=0 CELLSPACING=0>'."\n";
    print '<TR>'."\n";
    for (my $i=0;$i<$MAXSOURCES;$i++)
      {
	print '<TD ALIGN=center><TABLE BORDER="0">'."\n";
	print '<TR><TD ALIGN=center><a href="'.$SOURCENAME.($i+1).'.'.$SOUNDFORMAT.'"><img BORDER="0"   src ="'.$IMAGEPATH.$SOURCENAME.($i+1).'.'.$IMAGEFORMAT.'"></a></TD></TR>',"\n";
	print '<TR><TD ALIGN=center>',checkbox(-name=>($i+1),-label=>''),'</TD></TR>',"\n";
	print '</TABLE></TD>'."\n";
      }
    print '</TR></TABLE>'."\n";
    print submit('choose_sources','mix sources'),"\n",
      end_form,"\n";
    
  }

sub mix_sources
  {
    my @sources = ();
    my $source = 0;
    my $chosed_sources = '';
    my $mixargsin = '';
    my $mixargsout = '';
    my $icaargsin = '';
    my $icaargsout = '';
    my $calculate = 0;
    my $calculate_ica = 0;
    my $filename = '';
    
    my $j = 1;
    for (my $i = 1; $i <= $MAXSOURCES; $i++)
      {

	if (param($i))
	  {
	    push @sources,$i;
	    # pass on the information on the chosen sources
	    $chosed_sources .= '1';
	    # generate the list of arguments for ica
	    $mixargsin .= $SOURCENAME.$i.'.'.$SOUNDFORMAT.' ';
	    $mixargsout .= $MIXEDNAME.$j.'.'.$SOUNDFORMAT.' ';
	    $j++;
	  }
	else
	  {
	    $chosed_sources .= '0';
	  }
      }
    if ($#sources<1)
      {
	print p,strong('You have selected none or only one sound source. Please select at least two!'),p,"\n",
	start_form,submit('start_over','back'),"\n";
      }
    else
      {
	# check if the chosen sources have been mixed already
	$i = 1;

	foreach (@sources)
	  {
	    $filename = $chosed_sources.$MIXEDNAME.$i.'.'.$SOUNDFORMAT;
	    $icaargsin .= $filename.' ';
	    if (!(-e $filename))
	      { $calculate = 1; #print p,"Ei ole sekoitettu: $filename","\n" 
	      }
	    $filename = $chosed_sources.$ESTNAME.$i.'.'.$SOUNDFORMAT;
	    $icaargsout .= $filename.' ';
	    if (!(-e $filename))
	      { $calculate_ica = 1; #print p,"Ei ole laskettu: $filename","\n" 
	      }  
	    $i++;
	  }

	
	# mix sources 
	
	#kutsu Patrikin ohjelmaa, anna parametrina
	if ($calculate)
	  {
	    my $subs = $chosed_sources.'mix';
	    $mixargsout =~ s/mix/$subs/g;

	    #print p,'Kutsu: sekoita ',$mixargsin,' ',$mixargsout,p,"\n";
	    #print "Odota hetki, sekoitan lähteet...",p,"\n";
	    system("./sekoita $mixargsin $mixargsout");
	    
	    #print p,"Lasken ican taustalla",p,"\n";
	    #print p,'Kutsu: erottele ',$icaargsin,' ',$icaargsout,p,"\n";
	    system("./erottele $icaargsin $icaargsout&");

	    # tässä voisi jo alkaa laskea icaakin, mutta se pitäisi tehdä
	    # taustalla. No katsotaan...
	  }
	elsif ($calculate_ica)
	  {
	    #print p,"Sekoitteet oli, lasken ican taustalla",p,"\n";
	    #print p,'Kutsu: erottele ',$icaargsin,' ',$icaargsout,p,"\n";
	    system("./erottele $icaargsin $icaargsout&");
	  }


	print h2('ORIGINAL SOUND SOURCES'),"\n";
	print p,'By clicking the icons you can hear the original <A href="sounds.html">sound sources</A>.',"\n";
	print '<TABLE BORDER="0" CELLPADDING=0 CELLSPACING=0>'."\n";
	print '<TR>'."\n";
	foreach $source (@sources)
	  {
	    print '<TD ALIGN=center><a href="'.$SOURCENAME.($source).'.'.$SOUNDFORMAT.'"><img BORDER="0"   src ="'.$IMAGEPATH.$SOURCENAME.($source).'.'.$IMAGEFORMAT.'"></a></TD>',"\n";
	  }
	print '</TR></TABLE>'."\n";
	
	print h2('SAMPLES AT THE COCKTAIL PARTY'),"\n";
	
	print p,'By clicking the icons of the microphones you can listen to what the different microphones hear. The mixtures are all different, though some of them might sound quite similar.',"\n";
	
	my $i=1;
	print '<TABLE BORDER="0" CELLPADDING=0 CELLSPACING=0>'."\n";
	print '<TR>'."\n";
	foreach (@sources)
	  {
	    print '<TD ALIGN=center><a href="'.$chosed_sources.$MIXEDNAME.$i.'.'.$SOUNDFORMAT.'"><img BORDER="0"   src ="'.$IMAGEPATH.$MIXEDNAME.'.'.$IMAGEFORMAT.'"></a></TD>',"\n";
	    $i++;
	  }
	print '</TR></TABLE>',p,"\n";
	print start_form, 
	hidden(-name=>'list_of_chosen_sources',-default=>$chosed_sources),"\n",
	submit('mixed','separate the sound sources'),p,"\n";
      }
  }

sub show_results
  {
    my $binary = $ {pop @_};
    my @sources = split //,$binary;
    my $calculated = 0;
    my $filename = '';
    print h2('ORIGINAL SOUND SOURCES'),"\n";
    print p,'By clicking the icons you can listen to the original <A href="sounds.html">sound sources</A>.',"\n";
    
    my $i = 1;
    print '<TABLE BORDER="0" CELLPADDING=0 CELLSPACING=0>'."\n";
    print '<TR>'."\n";
    foreach $source (@sources)
      { 
	if ($source)
	  {
	    print '<TD ALIGN=center><a href="'.$SOURCENAME.$i.'.'.$SOUNDFORMAT.'"><img BORDER="0"   src ="'.$IMAGEPATH.$SOURCENAME.$i.'.'.$IMAGEFORMAT.'"></a></TD>',"\n";
	  }
	$i++;
      }	
    print '</TR></TABLE>',p,"\n";
    print "\n";

    # check that the sources are estimated and present
    while (!$calculated)
      {
	$calculated = 1;
	$i = 1;
	foreach $source (@sources)
	  { 
	    if ($source)
	      {
		$filename = $binary.$ESTNAME.$i.'.'.$SOUNDFORMAT;
		# print p,"Onko laskettu: $filename?","\n";
		if (!(-e $filename))
		  { 
		    $calculated = 0; 
		    # print p,"Ei ole laskettu: $filename","\n";
		  }
		$i++;
	      }	
	  }
	sleep 1;
      }

	print h2('SAMPLES AT THE COCKTAIL PARTY'),"\n";
	
	print p,'Listen to the mixtures by clicking the microphones.',p,"\n";
	
	my $i=1;
	print '<TABLE BORDER="0" CELLPADDING=0 CELLSPACING=0>'."\n";
	print '<TR>'."\n";
	foreach $source (@sources)
	  {
	    if ($source)
	      {
		print '<TD ALIGN=center><a href="'.$binary.$MIXEDNAME.$i.'.'.$SOUNDFORMAT.'"><img BORDER="0"   src ="'.$IMAGEPATH.$MIXEDNAME.'.'.$IMAGEFORMAT.'"></a></TD>',"\n";
		$i++;
	      }
	  }
	print '</TR></TABLE>',p,"\n";
  
    print h2('FOUND SOUND SOURCES'),"\n";
    print p,'Below are the the sound sources separated by ICA. Note that they might be in different order than the original ones.',p,"\n"; 
    $i = 1;
    print '<TABLE BORDER="0" CELLPADDING=0 CELLSPACING=0>'."\n";
    print '<TR>'."\n";
    foreach $source (@sources)
      { 
	if ($source)
	  {
	    print '<TD ALIGN=center><a href="'.$binary.$ESTNAME.$i.'.'.$SOUNDFORMAT.'"><img BORDER="0"   src ="'.$IMAGEPATH.$ESTNAME.'.'.$IMAGEFORMAT.'"></a></TD>',"\n";
	$i++;
	  }
      }	
    print '</TR></TABLE>',p,"\n";
    print p,start_form, submit('start_over','start over'),p,"\n";
  }

#### main ####

headers();

if (param('mixed'))
  {
    # sources have been mixed and listened 
    
    # show estimated sources
    # (possibly we have to estimate them here) and original sources
    
    # jos lähteet lasketaan jo aikaisemmin, täytyy nyt tarkastaa, että
    # ne on laskettu valmiiksi
    my $chosed_sources = param('list_of_chosen_sources');
    show_results(\$chosed_sources);
  }
elsif (!param('choose_sources'))
  {
    # sources not chosen, let her choose them
    choose_sources();
     }
else 
  {
    # the sources have been chosen, but the mixing has not been
    # calculated
    mix_sources();
  }

end_headers();
  
