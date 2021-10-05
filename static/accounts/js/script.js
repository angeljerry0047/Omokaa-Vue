$(document).ready(function(){
    var cropped_profile_pic='';
    var current = 0, current_step, next_step, steps;
    const WIDTH = $(window).width()
    if(WIDTH > 800){
    steps = $('fieldset').length;
    //get profile step
    $.ajax({
		url : '/account/step/',
        type: 'GET',
        data : {},
		success: function (data){
            
            console.log(data);
            current=data.step;
            if(current==0){
                current_step=$(".next:eq("+current+")").parent();
                current_step.show();
                setProgressBar(current);
            }
            else{
                var cc=current-1;
                current_step=$(".next:eq("+cc+")").parent();
                next_step=current_step.next();
                current_step.hide();
                next_step.show();
                setProgressBar(current);
            }
            if (data.user_type == '2') {
                $('#dateRegistration').html('Date of Registration');
                $('#uploadPhoto').html('Upload Logo');
                $('#uploadID').html('Upload Registration Certificate');
            }
		},
		error: function (error){
			
		}
    });

    
    
    
    
    $(".next").click(function () {
        if(!$(this).parent().find('input').val()) return;
        current_step = $(this).parent();
        next_step = $(this).parent().next();
        next_step.show();
        current_step.hide();
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
        console.log(curStep);
        var percent = 60+ parseFloat(40 / steps) * curStep;
        percent = percent.toFixed();
        $(".progress-bar")
            .css("width", percent + "%")
            .html(percent + "%");
    }

    $('input[type=radio][name=user_type]').change(function () {
        if (this.value == '2') {
            $('#dateRegistration').html('Date of Registration');
            $('#uploadPhoto').html('Upload Logo');
            $('#uploadID').html('Upload Registration Certificate');
        }
    });
    //update user information
    $("#extend_profile_form").submit(function(event){
        event.preventDefault(); //prevent default action 
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
                if(data.success){
                    console.log('success');
                }
                else{
                    console.log('error');
                }
                
            },
            error: function (error){
                
            }
        });

    
    
    });
    //crop image
    $image_crop = $('#image_demo').croppie({
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
      $('#profile_pic').on('change', function(){
        var reader = new FileReader();
        reader.onload = function (event) {
          $image_crop.croppie('bind', {
            url: event.target.result
          }).then(function(){
            console.log('jQuery bind complete');
          });
        }
        reader.readAsDataURL(this.files[0]);
        $('#cropimageModal').modal('show');
      });
    
      $('.crop_image').click(function(event){
        $image_crop.croppie('result', {
          type: 'canvas',
          size: 'viewport'
        }).then(function(response){
        $('#cropped_image').attr('src', response);
        fetch(response)
            .then(res => res.blob())
            .then(blob => {
            cropped_profile_pic = new File([blob], "filename.PNG");
        });
            $('#cropimageModal').modal('hide');
        })
      });
    }
})
