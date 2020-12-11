(function ($) {
    jQuery(document).ready(function ($) {
        $('#id_telefone').mask('(00) 0000-0000');
        $('#id_celular').mask('(00) 0.0000-0000');
        $("input[id$='-cep']").mask('00000-000');
        $("input[id$='-cep']").focusout(function () {
            $.ajax({
                url: 'https://viacep.com.br/ws/' + $(this).val() + '/json/unicode/',
                dataType: 'json',
                success: function (resposta) {
                    $("input[id$='-rua']").val(resposta.logradouro);
                    $("input[id$='-complemento']").val(resposta.complemento);
                    $("input[id$='-bairro']").val(resposta.bairro);
                    $("input[id$='-cidade']").val(resposta.localidade);
                    $("select[id$='-estado']").val(resposta.uf);
                    $("input[id$='-numero']").focus();
                }
            });
        });
    });
})(django.jQuery);