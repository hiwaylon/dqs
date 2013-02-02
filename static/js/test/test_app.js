describe('Score', function() {

  describe('The model', function() {
    it('Should exist as a model in the system.');
  });

  describe('The collection', function() {
    beforeEach(function() {
      $('body').append('<ul id="scores-template"></ul>');
      $('body').append('<ul id="score-template"></ul>');
      $('body').append('<ul id="new-food"></ul>');
    });

    it('Should have the correct url.', function() {
      scores = new DQS.Scores();
    });

  });

});