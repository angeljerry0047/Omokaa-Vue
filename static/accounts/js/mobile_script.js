$(document).ready(function(){
    var cropped_profile_pic='';
    var current = 0, current_step, next_step, steps;
    const WIDTH = $(window).width()
    if(WIDTH <= 800){ 
    steps = $('.fieldset_mobile').length;
    //get profile step
    $.ajax({
		url : '/account/step/',
        type: 'GET',
        data : {},
		success: function (data){
            current=data.step;
            if(current==0){
                current_step=$(".next_mobile:eq("+current+")").parent();
                current_step.show();
                setProgressBar(current);
            }
            else{
                var cc=current-1;
                current_step=$(".next_mobile:eq("+cc+")").parent();
                next_step=current_step.next();
                current_step.hide();
                next_step.show();
                setProgressBar(current);
            }
            if (data.user_type == '2') {
                $('#dateRegistration_mobile').html('Date of Registration');
                $('#uploadPhoto_mobile').html('Upload Logo');
                $('#uploadID_mobile').html('Upload Registration Certificate');
            }
		},
		error: function (error){
            console.log('api call')
			console.log(error)
		}
    });

    
    
    
    
    $(".next_mobile").click(function () {
        if(!$(this).parent().find('input').val()) return;
        current_step = $(this).parent();
        next_step = $(this).parent().next();
        next_step.show();
        current_step.hide();
        
        const currentInput = $(this)[0].attributes.current.value; 
        if(currentInput === 'user_type'){
            document.getElementById('formTitle').innerHTML = 'Date of Birth/Registeration'
        } 
        else if(currentInput === 'date_birth'){
            document.getElementById('formTitle').innerHTML = 'Upload your profile pic/logo'
        }
        else if(currentInput == 'profile_pic'){
            document.getElementById('formTitle').innerHTML = 'Upload your identity'
        }
        setProgressBar(++current);
        
    });
    $(".previous").click(function () {
        current_step = $(this).parent();
        next_step = $(this).parent().prev();
        next_step.show();
        current_step.hide();
        setProgressBar(--current);
    });
    

    // Change progress bar action
    function setProgressBar(curStep) {
        var percent = 60+ parseFloat(40 / steps) * curStep;
        percent = percent.toFixed();
        $(".progress-bar")
            .css("width", percent + "%")
            .html(percent + "%");
    }

    $('input[type=radio][name=user_type]').change(function () {
        if (this.value == '2') {
            $('#dateRegistration_mobile').html('Date of Registration');
            $('#uploadPhoto_mobile').html('Upload Logo');
            $('#uploadID_mobile').html('Upload Registration Certificate');
        }        
    });

    $("#extend_profile_form_mobile").submit(function(event){
        event.preventDefault(); //prevent default action 
        console.log(event.target)
        var post_url = $(this).attr("action"); //get form action url
        var request_method = $(this).attr("method"); //get form GET/POST method
        // var form_data = $(this).serialize(); //Encode form elements for submission
        var form_data = new FormData(this);
        if(cropped_profile_pic){
            form_data.append('cropped_profile_pic', cropped_profile_pic)
        }
        $.ajax({
            url : post_url,
            type: request_method,
            enctype: 'multipart/form-data',
            data : form_data,
            processData: false,
            contentType: false,
            cache: false,
            success: function (data){
                if(data.do_reload){
                    window.location.reload()
                }
            },
            error: function (error){
                
            }
        });

    
    
    });
    //crop image
    $image_crop_mobile = $('#image_demo_mobile').croppie({
        enableExif: true,
        viewport: {
          width:200,
          height:200,
          type:'circle' //circle
        },
        boundary:{
          width:300,
          height:300
        }
      });
      $('#profile_pic_mobile').on('change', function(){
        var reader = new FileReader();
        reader.onload = function (event) {
          $image_crop_mobile.croppie('bind', {
            url: event.target.result
          }).then(function(){
            console.log('jQuery bind complete');
          });
        }
        reader.readAsDataURL(this.files[0]);
        $('#cropimageModal_mobile').modal('show');
      });
    
      $('.crop_image_mobile').click(function(event){
        $image_crop_mobile.croppie('result', {
          type: 'canvas',
          size: 'viewport'
        }).then(function(response){
        $('#cropped_image_mobile').attr('src', response);
        fetch(response)
            .then(res => res.blob())
            .then(blob => {
            cropped_profile_pic = new File([blob], "filename.PNG");
        });
            $('#cropimageModal_mobile').modal('hide');
        })
      });
    }
})
